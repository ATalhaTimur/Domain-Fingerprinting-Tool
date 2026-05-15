<template>
  <div class="all-nodes">
    <!-- Empty state -->
    <div v-if="!scanData" class="empty">
      <div class="empty-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="5" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="5" r="2"/>
          <line x1="7" y1="5" x2="10" y2="10.5"/><line x1="14" y1="10.5" x2="17" y2="5"/>
        </svg>
      </div>
      <p>Run a scan to see discovered nodes</p>
    </div>

    <template v-else>
      <!-- Node count header -->
      <div class="list-header">
        <span class="list-label">Discovered Nodes</span>
        <span class="list-count">{{ sortedNodes.length }}</span>
      </div>

      <!-- Node rows -->
      <div
        v-for="n in sortedNodes"
        :key="n.id"
        class="item"
        :class="{ selected: n.id === selectedId, target: n.id === scanData.scan.target }"
        @click="emit('select-node', n.id)"
      >
        <div class="dot-wrap">
          <div class="dot" :style="{ background: dotColor(n) }" />
        </div>
        <div class="node-label" :title="n.id">{{ n.id }}</div>
        <div class="node-right">
          <span v-if="n.id === scanData.scan.target" class="target-badge">TARGET</span>
          <span v-else class="type-badge">{{ n.type.replace(/_/g, ' ') }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { NODE_COLORS, riskLevelLabel } from '../../composables/useScan.js'

const RISK_COLORS = { critical: '#ef4444', medium: '#f59e0b', low: '#10b981' }

const props = defineProps({ scanData: Object, selectedId: String })
const emit  = defineEmits(['select-node'])

const sortedNodes = computed(() => {
  if (!props.scanData) return []
  const target = props.scanData.scan.target
  return [...props.scanData.graph.nodes].sort((a, b) => {
    if (a.id === target) return -1
    if (b.id === target) return  1
    return a.type.localeCompare(b.type)
  })
})

function dotColor(n) {
  if (n.id === props.scanData?.scan.target) {
    const level = riskLevelLabel(props.scanData.scan.risk_score).cls
    return RISK_COLORS[level]
  }
  return NODE_COLORS[n.type] || '#888'
}
</script>

<style scoped>
.all-nodes { display: flex; flex-direction: column; gap: 2px; }

.empty {
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
.empty p { font-size: 0.8rem; text-align: center; line-height: 1.5; }

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 4px 10px;
  margin-bottom: 2px;
  border-bottom: 1px solid var(--border);
}
.list-label {
  font-size: 0.63rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.list-count {
  background: var(--bg-raised);
  color: var(--text-dim);
  font-size: 0.6rem;
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 600;
  border: 1px solid var(--border);
}

.item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.12s;
  border: 1px solid transparent;
}
.item:hover { background: var(--bg-raised); border-color: var(--border); }
.item.selected {
  background: rgba(59,130,246,0.07);
  border-color: rgba(59,130,246,0.25);
}
.item.target { }

.dot-wrap { flex-shrink: 0; }
.dot { width: 8px; height: 8px; border-radius: 50%; }

.node-label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.79rem;
  color: var(--text-secondary);
}
.item.selected .node-label { color: var(--accent-light); }

.node-right { flex-shrink: 0; }

.type-badge {
  font-size: 0.6rem;
  padding: 1px 6px;
  border-radius: 8px;
  background: var(--bg-raised);
  color: var(--text-dim);
  border: 1px solid var(--border);
  white-space: nowrap;
  text-transform: capitalize;
}
.target-badge {
  font-size: 0.58rem;
  padding: 1px 6px;
  border-radius: 8px;
  background: rgba(59,130,246,0.1);
  color: var(--accent-light);
  border: 1px solid rgba(59,130,246,0.2);
  font-weight: 700;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
</style>
