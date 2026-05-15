<template>
  <Transition name="slide">
    <div v-if="show" class="progress-panel">
      <div class="bar-wrap">
        <div class="bar-fill" :style="{ width: pct + '%' }" />
      </div>
      <div class="steps">
        <div
          v-for="step in steps"
          :key="step.id"
          class="chip"
          :class="states[step.id]"
        >
          <div class="dot" />
          {{ step.label }}
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({ show: Boolean, pct: Number, steps: Array, states: Object })
</script>

<style scoped>
.progress-panel {
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-surface);
  flex-shrink: 0;
}
.bar-wrap {
  height: 2px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 10px;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #818cf8, var(--green));
  background-size: 200% 100%;
  animation: shimmer 2s linear infinite;
  border-radius: 2px;
  transition: width 1.2s ease;
}
@keyframes shimmer { to { background-position: -200% 0; } }

.steps { display: flex; gap: 6px; flex-wrap: wrap; }
.chip {
  display: flex; align-items: center; gap: 5px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  border: 1px solid var(--border);
  background: var(--bg-raised);
  color: var(--text-dim);
  transition: all 0.3s ease;
}
.chip .dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--text-dim);
  transition: background 0.3s;
}
.chip.active { border-color: rgba(59,130,246,0.4); color: var(--accent-light); background: rgba(59,130,246,0.07); }
.chip.active .dot { background: var(--accent); animation: pulse 1s infinite; }
.chip.done   { border-color: rgba(16,185,129,0.3); color: var(--green); background: rgba(16,185,129,0.05); }
.chip.done .dot { background: var(--green); }

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.6); }
}

/* Transition */
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; max-height: 80px; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; padding-top: 0; padding-bottom: 0; }
</style>
