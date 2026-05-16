# AI Layer — Domain-Fingerprinting-Tool

## Overview

The AI layer sits between Graph Builder and Output. It consists of two components:

1. **DataPrepper** (`application/services/data_prepper.py`) — filters the graph, strips visual noise, produces compact relational text
2. **ClaudeAnalyzer** (`infrastructure/ai/claude_analyzer.py`) — sends the clean text to Claude API, returns an executive summary

In V1 the AI is a passive summarizer. In V2 it becomes the active orchestrator.

---

## DataPrepper

### Why it exists

NetworkX graph JSON is built for D3.js. It contains:

```json
{
  "nodes": [
    { "id": "example.com", "x": 342.18, "y": -119.44, "color": "#e74c3c", "radius": 12 }
  ],
  "edges": [
    { "source": "example.com", "target": "91.234.56.78", "relation": "resolves_to", "strokeWidth": 2 }
  ]
}
```

`x`, `y`, `color`, `radius`, `strokeWidth` — the model has zero use for these. They inflate token count and therefore cost without contributing any intelligence.

### What DataPrepper produces

```
example.com → 91.234.56.78 [resolves_to]
91.234.56.78 → evil-phish.ru [ip_neighbor]
91.234.56.78 → old-scam.net [ip_neighbor]
example.com → UA-99999999 [analytics_id]
UA-99999999 → evil-phish.ru [analytics_id_shared]
91.234.56.78 → 2ad2ad0002ad2ad00042d42d0000002ad2ad [jarm_hash]
2ad2ad0002ad2ad00042d42d0000002ad2ad → Cobalt Strike C2 [c2_match]
overall_risk_score: 84/100
domain_age: 8 days
jarm_c2_match: Cobalt Strike default
```

Domain age is formatted as human-readable text (`8 days`, `4 months`, `2 years, 3 months`) — never raw day counts.

Pure relational text. The model receives exactly what it needs: who is connected to what, and how.

### Token estimate

Average scan produces 20–40 relation lines ≈ 300–500 tokens. System prompt ≈ 200 tokens. Model response ≈ 400 tokens. Total per scan ≈ ~1000 tokens. Negligible cost.

---

## Prompts

Two modes. Same data. Different audiences.

Both prompts enforce a **fixed section structure** so every scan produces output in the same format. Claude cannot add sections, reorder them, or include "next steps" / "further investigation" language.

**Technical output structure:**
```
## Infrastructure Overview
## Threat Indicators
## Attribution Analysis
## Risk Assessment
```

**Executive output structure:**
```
## Summary
## Key Finding
## Business Impact
## Recommended Action
```

See `infrastructure/ai/prompts.py` for the full prompt text.

The user selects mode via a toggle in the frontend or `--mode` flag in CLI. The same DataPrepper output feeds both. No extra token cost — just a different system prompt.

---

## ClaudeAnalyzer

Implements `IAIAnalyzer` from `core/ports/ai_port.py`.

```python
# infrastructure/ai/claude_analyzer.py
import httpx, os
from core.ports.ai_port import IAIAnalyzer
from infrastructure.ai.prompts import PROMPTS

class ClaudeAnalyzer(IAIAnalyzer):
    MODEL = "claude-sonnet-4-20250514"

    async def analyze(self, relations_text: str, mode: str = "technical") -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key":         os.getenv("ANTHROPIC_API_KEY"),
                    "anthropic-version": "2023-06-01",
                    "content-type":      "application/json",
                },
                json={
                    "model":      self.MODEL,
                    "max_tokens": 512,
                    "system":     PROMPTS.get(mode, PROMPTS["technical"]),
                    "messages": [{
                        "role":    "user",
                        "content": f"Analyze the following infrastructure relationships:\n\n{relations_text}"
                    }]
                }
            )
        return r.json()["content"][0]["text"]
```

Because `ClaudeAnalyzer` implements `IAIAnalyzer`, it can be swapped for any other provider (GPT-4o, Gemini) without touching application or domain code.

---

## V1 → V2: from summarizer to orchestrator

### V1 (current)

```
Collector → Analyzer → Graph → DataPrepper → AI → Output
```

AI receives the finished graph and writes a summary. Passive. Always the same collectors run.

### V2 (LangGraph)

```
AI → decides which tools to call → tools execute → AI synthesizes → Output
```

The same Python collector functions become LangGraph tools. The AI decides the strategy:

```
AI sees DNS result: "A record is 104.21.x.x → Cloudflare is in front"
AI decision:        "JARM would fingerprint Cloudflare, not the origin server — skip it"
AI next call:       urlscan.io → get analytics IDs → find overlapping domains
```

This is the V2 agentic loop. No changes to domain entities, application services, or collector implementations. The orchestration layer changes from `asyncio.gather` to LangGraph. Clean Architecture makes this a clean swap.

```python
# V2 sketch — same WhoisCollector, wrapped as tool
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
async def whois_lookup(domain: str) -> dict:
    """Fetch WHOIS registration data for a domain."""
    return await WhoisCollector().fetch(domain)

tools  = [whois_lookup, dns_lookup, urlscan_lookup, crtsh_lookup, jarm_scan]
agent  = create_react_agent(model, tools)
result = await agent.ainvoke({"messages": [("user", f"Investigate {domain}")]})
```

V1 writes the tools. V2 hands them to an agent. Same functions, new orchestration.
