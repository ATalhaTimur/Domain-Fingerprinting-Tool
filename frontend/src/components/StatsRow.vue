<template>
  <div v-if="data" class="stats-row">
    <!-- Risk card -->
    <div class="card risk-card" :class="'risk-' + level.cls">
      <div class="card-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
      <div>
        <div class="label">Risk Score</div>
        <div class="value">{{ data.scan.risk_score }}<span class="value-sub">/100</span></div>
        <div class="chip" :class="level.cls">{{ level.label }}</div>
      </div>
    </div>

    <!-- Nodes card -->
    <div class="card">
      <div class="card-icon nodes-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><line x1="12" y1="9" x2="6.5" y2="6.5"/><line x1="12" y1="9" x2="17.5" y2="6.5"/><line x1="12" y1="15" x2="6.5" y2="17.5"/></svg></div>
      <div>
        <div class="label">Nodes</div>
        <div class="value">{{ data.graph.nodes.length }}</div>
        <div class="sub">discovered</div>
      </div>
    </div>

    <!-- Edges card -->
    <div class="card">
      <div class="card-icon edges-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div>
      <div>
        <div class="label">Edges</div>
        <div class="value">{{ data.graph.edges.length }}</div>
        <div class="sub">relationships</div>
      </div>
    </div>

    <!-- Mode card -->
    <div class="card">
      <div class="card-icon mode-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg></div>
      <div>
        <div class="label">Mode</div>
        <div class="value mode-val">{{ mode }}</div>
        <div class="sub">analysis type</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { riskLevelLabel } from '../composables/useScan.js'

const props = defineProps({ data: Object, mode: String })
const level = computed(() => riskLevelLabel(props.data?.scan.risk_score ?? 0))
</script>

<style scoped>
.stats-row {
  display: flex;
  gap: 10px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-base);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.card {
  flex: 1;
  min-width: 100px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  transition: border-color 0.15s;
}
.card:hover { border-color: var(--border-hover); }

.card-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: var(--bg-raised);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--text-muted);
}
.nodes-icon { color: var(--accent-light); }
.edges-icon { color: var(--purple); }
.mode-icon  { color: var(--text-muted); }

.label { font-size: 0.67rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 2px; }
.value { font-size: 1.3rem; font-weight: 700; color: var(--text-primary); line-height: 1.1; }
.value-sub { font-size: 0.65rem; color: var(--text-muted); font-weight: 400; margin-left: 1px; }
.sub  { font-size: 0.68rem; color: var(--text-dim); margin-top: 2px; }
.mode-val { font-size: 0.95rem; text-transform: capitalize; }

/* Risk chip */
.chip {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  margin-top: 3px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.chip.critical { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.chip.medium   { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
.chip.low      { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }

/* Risk card accent */
.risk-card { position: relative; overflow: hidden; }
.risk-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}
.risk-critical::before { background: linear-gradient(90deg, #ef4444, transparent); }
.risk-medium::before   { background: linear-gradient(90deg, #f59e0b, transparent); }
.risk-low::before      { background: linear-gradient(90deg, #10b981, transparent); }

.risk-critical .card-icon { color: #f87171; background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.15); }
.risk-medium   .card-icon { color: #fbbf24; background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.15); }
.risk-low      .card-icon { color: #34d399; background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.15); }
</style>
