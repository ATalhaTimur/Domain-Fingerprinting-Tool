<template>
  <div class="toolbar">
    <div class="input-wrap" :class="{ focused }">
      <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <input
        v-model="domain"
        type="text"
        placeholder="example.com or https://example.com"
        autocomplete="off"
        spellcheck="false"
        :disabled="scanning"
        @focus="focused = true"
        @blur="focused = false"
        @keydown.enter="emit('scan', domain)"
      />
      <button v-if="domain" class="clear-btn" @click="domain = ''" title="Clear">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <path d="M18 6 6 18M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div class="mode-toggle">
      <button :class="{ active: mode === 'technical' }" @click="emit('mode', 'technical')">
        Technical
      </button>
      <button :class="{ active: mode === 'executive' }" @click="emit('mode', 'executive')">
        Executive
      </button>
    </div>

    <button
      class="scan-btn"
      :disabled="scanning || !domain.trim()"
      @click="emit('scan', domain)"
    >
      <span v-if="scanning" class="spin-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83"/>
        </svg>
      </span>
      <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      {{ scanning ? 'Scanning…' : 'Scan' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({ mode: String, scanning: Boolean })
const emit   = defineEmits(['scan', 'mode'])
const domain = ref('')
const focused = ref(false)
</script>

<style scoped>
.toolbar {
  padding: 12px 20px;
  display: flex;
  gap: 10px;
  align-items: center;
  border-bottom: 1px solid var(--border);
  background: var(--bg-base);
  flex-shrink: 0;
}

/* Input */
.input-wrap {
  flex: 1;
  min-width: 220px;
  position: relative;
  display: flex;
  align-items: center;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-surface);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-wrap.focused {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}
.input-icon {
  position: absolute;
  left: 12px;
  color: var(--text-dim);
  pointer-events: none;
  flex-shrink: 0;
}
input {
  width: 100%;
  padding: 9px 36px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
}
input::placeholder { color: var(--text-dim); }
input:disabled { opacity: 0.5; }

.clear-btn {
  position: absolute;
  right: 8px;
  width: 22px; height: 22px;
  border-radius: 50%;
  border: none;
  background: var(--bg-raised);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
}
.clear-btn:hover { background: var(--border-hover); color: var(--text-primary); }

/* Mode toggle */
.mode-toggle {
  display: flex;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-surface);
}
.mode-toggle button {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.mode-toggle button:hover { color: var(--text-secondary); }
.mode-toggle button.active {
  background: linear-gradient(135deg, #1e3a5f, #152a48);
  color: var(--accent-light);
}

/* Scan button */
.scan-btn {
  padding: 9px 20px;
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  color: #fff;
  border: 1px solid rgba(96,165,250,0.3);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 7px;
  box-shadow: 0 1px 8px rgba(59,130,246,0.25);
}
.scan-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  box-shadow: 0 2px 16px rgba(59,130,246,0.4);
  transform: translateY(-1px);
}
.scan-btn:active:not(:disabled) { transform: translateY(0); }
.scan-btn:disabled { opacity: 0.45; cursor: not-allowed; box-shadow: none; }

.spin-icon { animation: spin 1s linear infinite; display: flex; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
