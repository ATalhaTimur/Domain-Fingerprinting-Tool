<template>
  <div class="side-panel">
    <!-- Tab bar -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <component :is="tab.icon" class="tab-icon" />
        {{ tab.label }}
        <span v-if="tab.badge" class="badge">{{ tab.badge }}</span>
      </button>
      <!-- animated underline indicator -->
      <div class="tab-indicator" :style="indicatorStyle" />
    </div>

    <!-- Pane area — absolute stacked, no layout shift -->
    <div class="pane-area">
      <div class="pane" :class="{ active: activeTab === 'node' }">
        <NodeInspector
          :node="selectedNode"
          :scan-data="scanData"
          :risk-score="scanData?.scan.risk_score"
          @select-node="onSelectNode"
        />
      </div>
      <div class="pane" :class="{ active: activeTab === 'nodes' }">
        <AllNodesList
          :scan-data="scanData"
          :selected-id="selectedNode?.id"
          @select-node="onSelectNode"
        />
      </div>
      <div class="pane" :class="{ active: activeTab === 'ai' }">
        <AiAnalysis :summary="scanData?.summary" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, h } from 'vue'
import NodeInspector from './NodeInspector.vue'
import AllNodesList  from './AllNodesList.vue'
import AiAnalysis    from './AiAnalysis.vue'

const props = defineProps({ scanData: Object })
const emit  = defineEmits(['node-selected'])

const activeTab    = ref('node')
const selectedNode = ref(null)

watch(() => props.scanData, () => {
  selectedNode.value = null
  activeTab.value    = 'node'
})

function onSelectNode(nodeId) {
  if (!props.scanData) return
  const node = props.scanData.graph.nodes.find(n => n.id === nodeId)
  if (node) { selectedNode.value = node; activeTab.value = 'node'; emit('node-selected', node) }
}

function selectNode(node) {
  selectedNode.value = node
  activeTab.value    = 'node'
}
defineExpose({ selectNode })

// SVG icons as render functions (no external deps)
const IconNode  = () => h('svg', { width:13, height:13, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'2' }, [h('circle',{cx:'12',cy:'12',r:'3'}),h('circle',{cx:'5',cy:'5',r:'2'}),h('circle',{cx:'19',cy:'5',r:'2'}),h('line',{x1:'12',y1:'9',x2:'6.5',y2:'6.5'}),h('line',{x1:'12',y1:'9',x2:'17.5',y2:'6.5'})])
const IconList  = () => h('svg', { width:13, height:13, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'2' }, [h('line',{x1:'8',y1:'6',x2:'21',y2:'6'}),h('line',{x1:'8',y1:'12',x2:'21',y2:'12'}),h('line',{x1:'8',y1:'18',x2:'21',y2:'18'}),h('line',{x1:'3',y1:'6',x2:'3.01',y2:'6'}),h('line',{x1:'3',y1:'12',x2:'3.01',y2:'12'}),h('line',{x1:'3',y1:'18',x2:'3.01',y2:'18'})])
const IconAI    = () => h('svg', { width:13, height:13, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'2' }, [h('path',{d:'M12 2a10 10 0 1 0 10 10'}),h('path',{d:'M12 6v6l4 2'})])

const TAB_DEFS = [
  { id: 'node',  label: 'Node',      icon: IconNode },
  { id: 'nodes', label: 'All Nodes', icon: IconList },
  { id: 'ai',    label: 'AI',        icon: IconAI   },
]

const tabs = computed(() => TAB_DEFS.map(t => ({
  ...t,
  badge: t.id === 'nodes' && props.scanData?.graph.nodes.length
    ? props.scanData.graph.nodes.length
    : t.id === 'ai' && props.scanData?.summary ? '✦' : null
})))

const TAB_IDS = ['node', 'nodes', 'ai']
const indicatorStyle = computed(() => {
  const idx = TAB_IDS.indexOf(activeTab.value)
  return {
    transform: `translateX(${idx * 100}%)`,
    width: `${100 / TAB_IDS.length}%`,
  }
})
</script>

<style scoped>
.side-panel {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border);
  background: var(--bg-surface);
  overflow: hidden;
}

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  position: relative;
  background: var(--bg-base);
}

.tab {
  flex: 1;
  padding: 11px 4px;
  border: none;
  background: transparent;
  color: var(--text-dim);
  font-size: 0.73rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: color 0.15s;
  position: relative;
  z-index: 1;
}
.tab:hover { color: var(--text-muted); }
.tab.active { color: var(--accent-light); }
.tab-icon { flex-shrink: 0; }

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent-light));
  border-radius: 1px;
  transition: transform 0.25s cubic-bezier(.4,0,.2,1);
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px; height: 16px;
  padding: 0 4px;
  border-radius: 8px;
  background: rgba(59,130,246,0.15);
  color: var(--accent-light);
  font-size: 0.58rem;
  font-weight: 700;
  border: 1px solid rgba(59,130,246,0.2);
}

/* Pane area */
.pane-area { flex: 1; position: relative; min-height: 0; overflow: hidden; }

.pane {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease;
}
.pane.active { opacity: 1; pointer-events: all; }
</style>
