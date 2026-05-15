import { ref, computed } from 'vue'

const SCAN_STEPS = [
  { id: 'whois',   label: 'WHOIS',       delay: 0     },
  { id: 'dns',     label: 'DNS',         delay: 3000  },
  { id: 'jarm',    label: 'JARM/TLS',    delay: 7000  },
  { id: 'crtsh',   label: 'crt.sh',      delay: 11000 },
  { id: 'ht',      label: 'IP Scan',     delay: 15000 },
  { id: 'urlscan', label: 'URLScan',     delay: 18000 },
  { id: 'ai',      label: 'AI Analysis', delay: 22000 },
  { id: 'graph',   label: 'Graph',       delay: 26000 },
]

export function riskLevelLabel(score) {
  if (score >= 70) return { cls: 'critical', label: 'Critical' }
  if (score >= 40) return { cls: 'medium',   label: 'Medium'   }
  return { cls: 'low', label: 'Low' }
}

export const NODE_COLORS = {
  domain:       '#4a9eff',
  ip:           '#5dade2',
  analytics_id: '#a569bd',
  jarm_hash:    '#f39c12',
  c2_name:      '#e74c3c',
}

export function useScan() {
  const mode        = ref('technical')
  const scanning    = ref(false)
  const scanData    = ref(null)
  const error       = ref(null)
  const scanElapsed = ref('')

  // step state: 'idle' | 'active' | 'done'
  const stepStates  = ref(Object.fromEntries(SCAN_STEPS.map(s => [s.id, 'idle'])))
  const progressPct = ref(0)
  let stepTimers    = []

  function setMode(m) { mode.value = m }

  function _startProgress() {
    stepStates.value  = Object.fromEntries(SCAN_STEPS.map(s => [s.id, 'idle']))
    progressPct.value = 0
    stepTimers = []

    SCAN_STEPS.forEach((step, idx) => {
      const t = setTimeout(() => {
        if (idx > 0) stepStates.value[SCAN_STEPS[idx - 1].id] = 'done'
        stepStates.value[step.id] = 'active'
        progressPct.value = Math.round(((idx + 1) / SCAN_STEPS.length) * 88)
      }, step.delay)
      stepTimers.push(t)
    })
  }

  function _finishProgress() {
    stepTimers.forEach(clearTimeout)
    stepTimers = []
    SCAN_STEPS.forEach(s => { stepStates.value[s.id] = 'done' })
    progressPct.value = 100
    setTimeout(() => { progressPct.value = -1 }, 800) // -1 = hide panel
  }

  function _clearProgress() {
    stepTimers.forEach(clearTimeout)
    stepTimers = []
    progressPct.value = -1
  }

  async function startScan(domain) {
    if (!domain.trim() || scanning.value) return

    scanning.value = true
    scanData.value = null
    error.value    = null
    scanElapsed.value = ''
    const t0 = Date.now()

    _startProgress()

    try {
      const res = await fetch('http://localhost:8000/api/v1/scan', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ target: domain.trim(), mode: mode.value }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }))
        throw new Error(err.error || res.statusText)
      }

      scanData.value    = await res.json()
      scanElapsed.value = ((Date.now() - t0) / 1000).toFixed(1) + 's'
      _finishProgress()
    } catch (e) {
      error.value = e.message
      _clearProgress()
    } finally {
      scanning.value = false
    }
  }

  const showProgress = computed(() => progressPct.value >= 0 && progressPct.value <= 100)
  const steps        = SCAN_STEPS

  return {
    mode, scanning, scanData, error, scanElapsed,
    stepStates, progressPct, showProgress, steps,
    setMode, startScan,
  }
}
