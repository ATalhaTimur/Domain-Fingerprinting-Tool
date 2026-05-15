<template>
  <header>
    <div class="logo">
      <div class="logo-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
      </div>
      <span class="logo-text">DFT</span>
      <span class="logo-divider" />
      <span class="logo-sub">Domain Fingerprinting</span>
    </div>
    <div class="spacer" />
    <div class="hint">
      <kbd>↵</kbd> to scan
    </div>
  </header>
</template>

<style scoped>
header {
  padding: 0 24px;
  height: 52px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-surface);
  flex-shrink: 0;
  position: relative;
}

/* subtle gradient line at bottom */
header::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, var(--accent) 0%, transparent 60%);
  opacity: 0.5;
}

.logo { display: flex; align-items: center; gap: 10px; }

.logo-icon {
  width: 30px; height: 30px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1e3a5f, #0d1a2e);
  border: 1px solid var(--border-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-light);
  flex-shrink: 0;
}

.logo-text {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.08em;
}

.logo-divider {
  width: 1px;
  height: 16px;
  background: var(--border);
}

.logo-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 400;
}

.spacer { flex: 1; }

.hint {
  font-size: 0.72rem;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 5px;
}

kbd {
  font-family: inherit;
  font-size: 0.68rem;
  background: var(--bg-raised);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 6px;
  color: var(--text-muted);
  box-shadow: 0 1px 0 var(--border);
}
</style>
