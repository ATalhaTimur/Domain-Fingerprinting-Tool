<template>
  <div class="app">
    <!-- Global tooltip (used by D3 graph.js) -->
    <div id="dft-tooltip" class="tooltip">
      <div id="tt-id" class="tt-id"></div>
      <div id="tt-type" class="tt-type"></div>
    </div>

    <AppHeader />

    <ScanToolbar
      :mode="mode"
      :scanning="scanning"
      @scan="startScan"
      @mode="setMode"
      @example="startScan"
    />

    <ProgressPanel
      :show="showProgress"
      :pct="progressPct"
      :steps="steps"
      :states="stepStates"
    />

    <StatsRow   :data="scanData" :mode="mode" />
    <TargetBanner :data="scanData" :elapsed="scanElapsed" />

    <div class="workspace">
      <GraphView
        :data="scanData"
        :error="error"
        @node-click="onNodeClick"
        @example="startScan"
      />

      <SidePanel ref="sidePanel" :scan-data="scanData" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useScan } from './composables/useScan.js'

import AppHeader    from './components/AppHeader.vue'
import ScanToolbar  from './components/ScanToolbar.vue'
import ProgressPanel from './components/ProgressPanel.vue'
import StatsRow     from './components/StatsRow.vue'
import TargetBanner from './components/TargetBanner.vue'
import GraphView    from './components/GraphView.vue'
import SidePanel    from './components/SidePanel/SidePanel.vue'

const {
  mode, scanning, scanData, error, scanElapsed,
  stepStates, progressPct, showProgress, steps,
  setMode, startScan,
} = useScan()

const sidePanel = ref(null)

function onNodeClick(node) {
  sidePanel.value?.selectNode(node)
}
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.workspace {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}
</style>

<style>
/* Global tooltip (accessed by D3 via plain DOM id) */
.tooltip {
  position: fixed;
  pointer-events: none;
  z-index: 100;
  background: rgba(22,27,34,0.96);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.78rem;
  color: var(--text-secondary);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  display: none;
  max-width: 220px;
}
.tt-id   { font-weight: 600; color: var(--text-primary); word-break: break-all; margin-bottom: 3px; }
.tt-type { font-size: 0.7rem; color: var(--text-muted); }
</style>
