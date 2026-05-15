<template>
  <div class="inspector">
    <!-- Empty state -->
    <div v-if="!node" class="empty">
      <div class="empty-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
      </div>
      <p>Click a node to inspect</p>
    </div>

    <template v-else>
      <!-- Node header -->
      <div class="node-header">
        <div class="node-dot" :style="{ background: nodeColor }" />
        <div class="node-info">
          <div class="node-id">{{ node.id }}</div>
          <span class="type-badge">{{ node.type.replace(/_/g, ' ') }}</span>
        </div>
      </div>

      <!-- Risk (target only) -->
      <div v-if="isTarget" class="section">
        <div class="section-title">Risk Assessment</div>
        <div class="risk-bar-wrap">
          <div class="risk-bar-track">
            <div class="risk-bar-fill" :class="level.cls" :style="{ width: riskScore + '%' }" />
          </div>
          <span class="risk-score" :class="level.cls">{{ riskScore }}/100</span>
        </div>
        <span class="risk-chip" :class="level.cls">{{ level.label }} Risk</span>
      </div>

      <!-- Connections -->
      <div class="section">
        <div class="section-title">Connections <span class="count">{{ connections.length }}</span></div>
        <div v-if="!connections.length" class="empty-row">No connections</div>
        <div
          v-for="c in connections"
          :key="c.dir + c.id"
          class="conn-row"
          @click="emit('select-node', c.id)"
        >
          <span class="conn-dir" :class="c.dir === '→' ? 'out' : 'in'">{{ c.dir }}</span>
          <span class="conn-id">{{ c.id }}</span>
          <span class="conn-rel">{{ c.rel.replace(/_/g, ' ') }}</span>
        </div>
      </div>

      <!-- Metadata -->
      <div class="section">
        <div class="section-title">Metadata</div>
        <div v-if="!metaEntries.length" class="empty-row">No metadata</div>
        <div v-for="[k, v] in metaEntries" :key="k" class="meta-row">
          <span class="meta-key">{{ k }}</span>
          <span class="meta-val">{{ typeof v === 'object' ? JSON.stringify(v) : String(v) }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { riskLevelLabel, NODE_COLORS } from '../../composables/useScan.js'

const RISK_COLORS = { critical: '#ef4444', medium: '#f59e0b', low: '#10b981' }

const props = defineProps({ node: Object, scanData: Object, riskScore: Number })
const emit  = defineEmits(['select-node'])

const isTarget   = computed(() => props.node?.id === props.scanData?.scan.target)
const level      = computed(() => riskLevelLabel(props.riskScore ?? 0))
const nodeColor  = computed(() => {
  if (!props.node) return '#888'
  if (isTarget.value) return RISK_COLORS[level.value.cls]
  return NODE_COLORS[props.node.type] || '#888'
})
const connections = computed(() => {
  if (!props.node || !props.scanData) return []
  const res = []
  props.scanData.graph.edges.forEach(e => {
    if (e.source === props.node.id) res.push({ dir: '→', id: e.target, rel: e.relation })
    if (e.target === props.node.id) res.push({ dir: '←', id: e.source, rel: e.relation })
  })
  return res
})
const metaEntries = computed(() => props.node?.metadata ? Object.entries(props.node.metadata) : [])
</script>

<style scoped>
.inspector { display: flex; flex-direction: column; gap: 16px; }

.empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 20px;
  color: var(--text-dim);
}
.empty-icon {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: var(--bg-raised);
  border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-dim);
}
.empty p { font-size: 0.8rem; text-align: center; }

/* Node header */
.node-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--bg-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}
.node-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.node-info { flex: 1; min-width: 0; }
.node-id {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
  line-height: 1.4;
}
.type-badge {
  display: inline-block;
  font-size: 0.65rem;
  padding: 1px 7px;
  border-radius: 8px;
  background: var(--bg-base);
  color: var(--text-muted);
  border: 1px solid var(--border);
  margin-top: 3px;
  text-transform: capitalize;
}

/* Sections */
.section { display: flex; flex-direction: column; gap: 6px; }
.section-title {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  display: flex;
  align-items: center;
  gap: 6px;
}
.count {
  background: var(--bg-raised);
  color: var(--text-dim);
  font-size: 0.6rem;
  padding: 1px 5px;
  border-radius: 6px;
  font-weight: 600;
}

/* Risk bar */
.risk-bar-wrap { display: flex; align-items: center; gap: 8px; }
.risk-bar-track {
  flex: 1;
  height: 5px;
  background: var(--bg-raised);
  border-radius: 3px;
  overflow: hidden;
}
.risk-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s cubic-bezier(.4,0,.2,1);
}
.risk-bar-fill.critical { background: linear-gradient(90deg, #ef4444, #dc2626); }
.risk-bar-fill.medium   { background: linear-gradient(90deg, #f59e0b, #d97706); }
.risk-bar-fill.low      { background: linear-gradient(90deg, #10b981, #059669); }

.risk-score {
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}
.risk-score.critical { color: #f87171; }
.risk-score.medium   { color: #fbbf24; }
.risk-score.low      { color: #34d399; }

.risk-chip {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  align-self: flex-start;
}
.risk-chip.critical { background: rgba(239,68,68,0.1);  color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.risk-chip.medium   { background: rgba(245,158,11,0.1); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
.risk-chip.low      { background: rgba(16,185,129,0.1); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }

/* Connections */
.conn-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.12s;
  border: 1px solid transparent;
}
.conn-row:hover { background: var(--bg-raised); border-color: var(--border); }
.conn-dir {
  font-size: 0.75rem;
  font-weight: 700;
  width: 16px;
  text-align: center;
  flex-shrink: 0;
}
.conn-dir.out { color: var(--accent-light); }
.conn-dir.in  { color: var(--purple); }
.conn-id {
  flex: 1;
  font-size: 0.78rem;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.conn-rel { font-size: 0.65rem; color: var(--text-dim); white-space: nowrap; flex-shrink: 0; }

/* Metadata */
.meta-row {
  display: flex;
  gap: 8px;
  padding: 5px 8px;
  border-radius: 5px;
  font-size: 0.76rem;
  border-bottom: 1px solid var(--border);
}
.meta-row:last-child { border-bottom: none; }
.meta-key { color: var(--text-muted); width: 38%; flex-shrink: 0; font-weight: 500; }
.meta-val { color: var(--text-secondary); word-break: break-all; }

.empty-row { font-size: 0.76rem; color: var(--text-dim); padding: 6px 8px; }
</style>
