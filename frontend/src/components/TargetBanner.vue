<template>
  <div v-if="data" class="banner">
    <div class="pulse-wrap">
      <div class="pulse-ring" />
      <div class="pulse-dot" />
    </div>
    <div class="info">
      <span class="label">Active Target</span>
      <span class="domain">{{ data.scan.target }}</span>
    </div>
    <div class="spacer" />
    <div v-if="elapsed" class="elapsed">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
      </svg>
      {{ elapsed }}
    </div>
  </div>
</template>

<script setup>
defineProps({ data: Object, elapsed: String })
</script>

<style scoped>
.banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 20px;
  height: 50px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(90deg, rgba(16,185,129,0.05) 0%, transparent 50%);
  flex-shrink: 0;
}

.pulse-wrap {
  position: relative;
  width: 12px; height: 12px;
  flex-shrink: 0;
}
.pulse-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--green);
  position: absolute;
  top: 2px; left: 2px;
  box-shadow: 0 0 8px var(--green);
}
.pulse-ring {
  width: 12px; height: 12px;
  border-radius: 50%;
  border: 1px solid var(--green);
  position: absolute;
  top: 0; left: 0;
  animation: ripple 2s ease-out infinite;
  opacity: 0;
}
@keyframes ripple {
  0%   { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(2.5); opacity: 0; }
}

.info { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.label { font-size: 0.62rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.08em; }
.domain {
  font-size: 1.1rem;
  font-weight: 700;
  font-family: "SF Mono", "Cascadia Code", "Fira Code", monospace;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spacer { flex: 1; }

.elapsed {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  color: var(--text-dim);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 3px 10px;
  flex-shrink: 0;
}
</style>
