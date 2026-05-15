<template>
  <div class="ai-analysis">
    <!-- Empty state -->
    <div v-if="!html" class="empty">
      <div class="empty-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 2a10 10 0 1 0 10 10"/><path d="M12 6v6l4 2"/>
          <path d="M20 2v4m0 0h-4m4 0-5 5"/>
        </svg>
      </div>
      <p>AI analysis will appear<br>after a scan completes</p>
    </div>

    <!-- Analysis content -->
    <template v-else>
      <div class="ai-header">
        <div class="ai-badge">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M12 2a10 10 0 1 0 10 10"/><path d="M12 6v6l4 2"/>
          </svg>
          AI Analysis
        </div>
      </div>
      <div class="md" v-html="html" />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

marked.use({ gfm: true, breaks: true })

const props = defineProps({ summary: String })
const html  = computed(() => props.summary ? marked.parse(props.summary) : '')
</script>

<style scoped>
.ai-analysis { display: flex; flex-direction: column; gap: 14px; }

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

.ai-header { display: flex; align-items: center; }
.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.63rem;
  font-weight: 700;
  color: var(--accent-light);
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.18);
  border-radius: 20px;
  padding: 3px 10px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
</style>
