<template>
  <div class="graph-wrap">
    <!-- Empty state -->
    <Transition name="fade">
      <div v-if="!data && !error" class="empty-state">
        <div class="empty-card">
          <div class="empty-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="1.5">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 2v2m0 16v2M2 12h2m16 0h2"/>
              <path d="m4.93 4.93 1.41 1.41m11.32 11.32 1.41 1.41M4.93 19.07l1.41-1.41m11.32-11.32 1.41-1.41"/>
            </svg>
          </div>
          <h2>Start Fingerprinting</h2>
          <p>Enter a domain to map its DNS, WHOIS, TLS fingerprint, subdomains and IP neighbors.</p>
          <div class="examples">
            <button v-for="d in examples" :key="d" class="ex-btn" @click="emit('example', d)">{{ d }}</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Error state -->
    <Transition name="fade">
      <div v-if="error" class="empty-state">
        <div class="empty-card error-card">
          <div class="empty-icon error-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/>
            </svg>
          </div>
          <h2 style="color:var(--red)">Scan failed</h2>
          <p>{{ error }}</p>
        </div>
      </div>
    </Transition>

    <!-- D3 canvas -->
    <div ref="graphEl" class="graph-canvas" />

    <!-- Legend -->
    <Transition name="fade">
      <div v-if="data" class="legend">
        <div class="legend-title">Node Types</div>
        <div v-for="(color, type) in NODE_COLORS" :key="type" class="legend-item">
          <div class="legend-dot" :style="{ background: color }" />
          <span>{{ type.replace(/_/g, ' ') }}</span>
        </div>
      </div>
    </Transition>

    <!-- Zoom controls -->
    <Transition name="fade">
      <div v-if="data" class="zoom-controls">
        <button class="ctrl" title="Zoom in"  @click="zoomBy(1.4)">+</button>
        <button class="ctrl" title="Zoom out" @click="zoomBy(1/1.4)">−</button>
        <button class="ctrl" title="Fit"      @click="zoomReset">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { renderGraph } from '../graph.js'
import { NODE_COLORS } from '../composables/useScan.js'

const props = defineProps({ data: Object, error: String })
const emit  = defineEmits(['node-click', 'example'])

const examples    = ['github.com', 'cloudflare.com', 'stripe.com']
const graphEl     = ref(null)
let svgNode       = null
let zoomBehavior  = null

watch(() => props.data, async (newData) => {
  if (!newData) return
  await nextTick()
  const result     = renderGraph(graphEl.value, newData, (node) => emit('node-click', node))
  svgNode          = result.svg
  zoomBehavior     = result.zoom
}, { immediate: true })

function zoomBy(factor) {
  if (!svgNode || !zoomBehavior) return
  zoomBehavior.scaleBy(d3.select(svgNode).transition().duration(250), factor)
}
function zoomReset() {
  if (!svgNode || !zoomBehavior) return
  zoomBehavior.transform(d3.select(svgNode).transition().duration(350), d3.zoomIdentity)
}
</script>

<style scoped>
.graph-wrap {
  flex: 1;
  position: relative;
  background: var(--bg-base);
  min-height: 0;
  overflow: hidden;
}
.graph-canvas { position: absolute; inset: 0; }

/* Empty / Error state */
.empty-state {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  z-index: 2;
}
.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  max-width: 300px;
  text-align: center;
  padding: 36px 32px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
.error-card { border-color: rgba(239,68,68,0.2); }

.empty-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.15);
  display: flex; align-items: center; justify-content: center;
}
.error-icon { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.15); }

.empty-card h2 { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); }
.empty-card p  { font-size: 0.78rem; color: var(--text-muted); line-height: 1.6; }

.examples { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.ex-btn {
  padding: 5px 12px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--bg-raised);
  color: var(--text-muted);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}
.ex-btn:hover { border-color: var(--accent); color: var(--accent-light); background: rgba(59,130,246,0.07); }

/* Legend */
.legend {
  position: absolute; bottom: 16px; left: 16px;
  background: rgba(17,24,39,0.92);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  display: flex; flex-direction: column; gap: 7px;
  z-index: 10;
  backdrop-filter: blur(8px);
  box-shadow: var(--shadow-sm);
}
.legend-title { font-size: 0.63rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.08em; }
.legend-item  { display: flex; align-items: center; gap: 8px; font-size: 0.73rem; color: var(--text-secondary); }
.legend-dot   { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* Zoom controls */
.zoom-controls {
  position: absolute; bottom: 16px; right: 16px;
  display: flex; flex-direction: column; gap: 4px;
  z-index: 10;
}
.ctrl {
  width: 30px; height: 30px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: rgba(17,24,39,0.92);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 15px;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(8px);
  transition: all 0.15s;
}
.ctrl:hover { border-color: var(--border-hover); color: var(--text-primary); background: var(--bg-raised); }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
