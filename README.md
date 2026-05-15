# Domain-Fingerprinting-Tool 🔍

> **Domain Fingerprinting Tool** — One signal in. The whole adversarial network out.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is Domain-Fingerprinting-Tool?

Domain-Fingerprinting-Tool takes a single domain, URL, or IP address and traces it back to its full adversarial network. It maps shared infrastructure, overlapping identities, and coordinated threat operations — the difference between cutting a branch and pulling a root.

Detection tools catch the artifact. Domain-Fingerprinting-Tool exposes the system behind it.

---

## How it works

```
Input (domain / URL / IP)
        │
        ▼
Cache Shield (SQLite dev / Redis prod) ── HIT ──▶ skip to Output
        │ MISS
        ▼
Collector Layer  (all I/O, fully async — asyncio.gather)
  ├── WHOIS          asyncwhois
  ├── DNS            dns.asyncresolver
  ├── urlscan.io     httpx async
  ├── crt.sh         asyncpg  (direct PostgreSQL, unlimited free)
  ├── HackerTarget   httpx async
  └── JARM           asyncio.to_thread()  ← sync lib, isolated
        │
        ▼
Analyzer Layer  (zero I/O — pure domain logic)
  ├── Analytics ID overlap   (same GA/GTM = same operator)
  ├── TLS + IP correlation   (subdomain / neighbor linking)
  └── JARM matching          (hash vs C2 list → risk score 0–100)
        │
        ▼
Graph Builder  (NetworkX → nodes + edges → JSON)
        │
        ▼
Data Prepper  (strip coordinates/colors → pure relational text)
        │
        ▼
AI Analyzer  (Claude API)
  ├── Technical mode   →  senior threat analyst tone
  └── Executive mode   →  CISO briefing tone
        │
        ▼
Output
  ├── Interactive graph   D3.js  (Vercel)
  ├── REST API            FastAPI (Render.com)
  └── CLI                 typer
```

---

## Project structure

Clean Architecture with DDD layering. Dependency rule: outer layers depend on inner layers, never the reverse.

```
Domain-Fingerprinting-Tool/
│
├── core/                          # Enterprise business rules — no dependencies
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── scan.py            # Scan aggregate root
│   │   │   ├── domain_target.py   # DomainTarget value object
│   │   │   ├── threat_graph.py    # ThreatGraph entity
│   │   │   └── risk_score.py      # RiskScore value object
│   │   ├── events/
│   │   │   ├── scan_completed.py
│   │   │   └── threat_detected.py
│   │   └── exceptions/
│   │       ├── invalid_domain.py
│   │       └── scan_failed.py
│   └── ports/                     # Abstract interfaces (contracts)
│       ├── collector_port.py      # ICollector ABC
│       ├── cache_port.py          # ICache ABC
│       ├── ai_port.py             # IAIAnalyzer ABC
│       └── graph_port.py          # IGraphBuilder ABC
│
├── application/                   # Application business rules — orchestration
│   ├── use_cases/
│   │   ├── scan_domain.py         # ScanDomainUseCase
│   │   ├── get_scan_result.py     # GetScanResultUseCase
│   │   └── build_threat_graph.py  # BuildThreatGraphUseCase
│   ├── services/
│   │   ├── collector_service.py   # asyncio.gather orchestration
│   │   ├── analyzer_service.py    # pure analysis logic
│   │   └── data_prepper.py        # graph → LLM-ready text
│   └── dto/
│       ├── scan_request.py        # ScanRequestDTO
│       └── scan_response.py       # ScanResponseDTO
│
├── infrastructure/                # Frameworks & drivers — all I/O lives here
│   ├── cache/
│   │   ├── sqlite_cache.py        # ICache → SQLite (dev)
│   │   └── redis_cache.py         # ICache → Redis (prod)
│   ├── ai/
│   │   ├── claude_analyzer.py     # IAIAnalyzer → Claude API
│   │   └── prompts.py             # technical / executive prompts
│   └── external_apis/
│       ├── whois_collector.py     # ICollector → asyncwhois
│       ├── dns_collector.py       # ICollector → dns.asyncresolver
│       ├── urlscan_collector.py   # ICollector → urlscan.io httpx
│       ├── crtsh_collector.py     # ICollector → asyncpg PostgreSQL
│       ├── hackertarget_collector.py  # ICollector → httpx
│       ├── jarm_collector.py      # ICollector → asyncio.to_thread
│       └── networkx_graph.py      # IGraphBuilder → NetworkX
│
├── api/                           # Delivery mechanism — FastAPI
│   ├── routes/
│   │   ├── scan.py                # POST /api/v1/scan
│   │   └── health.py              # GET  /api/v1/health
│   ├── middleware/
│   │   ├── rate_limiter.py
│   │   └── error_handler.py
│   └── main.py                    # FastAPI app factory
│
├── cli/
│   └── commands.py                # typer CLI entry point
│
├── tests/
│   ├── unit/
│   │   ├── core/
│   │   │   └── test_risk_score.py
│   │   └── application/
│   │       ├── test_analyzer_service.py
│   │       └── test_data_prepper.py
│   ├── integration/
│   │   ├── test_whois_collector.py
│   │   └── test_crtsh_collector.py
│   └── e2e/
│       └── test_scan_domain.py
│
├── frontend/
│   ├── index.html
│   └── graph.js                   # D3.js visualization
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COLLECTORS.md
│   ├── AI_LAYER.md
│   └── DEPLOYMENT.md
│
├── pyproject.toml                 # dependencies + tooling config
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Features (V1)

- **Async-first** — all collectors run concurrently via `asyncio.gather()`
- **Cache shield** — sits between input and collectors, API limits never wasted
- **JARM fingerprinting** — TLS stack identification (Cloudflare? bare Nginx? C2 malware?)
- **crt.sh integration** — unlimited free subdomain/TLS overlap via direct PostgreSQL
- **Analytics ID overlap** — same GA/GTM code across sites = same operator
- **AI-powered summary** — Claude API turns raw graph into actionable intelligence
- **Dual output mode** — technical analyst or executive CISO briefing
- **Zero infra cost** — Render.com (backend) + Vercel (frontend)
- **Clean Architecture** — DDD layering, ports & adapters, fully testable

---

## Roadmap

| Version | Description |
|---------|-------------|
| **V1** | Pipeline — static, all collectors run in parallel, AI summarizes at the end |
| **V2** | Agentic Decision Engine — LangGraph orchestrates collectors as tools, AI decides what to query and when |

In V2, if the AI sees Cloudflare on DNS it skips JARM and jumps to urlscan analytics. The Python functions from V1 become LangGraph tools — zero refactor, same domain logic.

---

## Quick start

```bash
git clone https://github.com/ATalhaTimur/Domain-Fingerprinting-Tool
cd Domain-Fingerprinting-Tool
pip install -e ".[dev]"
cp .env.example .env        # add your API keys
python -m cli.commands scan example.com --mode technical
```

Or with Docker:

```bash
docker compose up
```

---

## API keys needed

| Service | Free tier | Where to get |
|---------|-----------|--------------|
| urlscan.io | 100 scans/day | [urlscan.io/user/signup](https://urlscan.io/user/signup/) |
| VirusTotal | 500 req/day, 4 req/min | [virustotal.com](https://www.virustotal.com/) |
| HackerTarget | ~100 req/day | [hackertarget.com](https://hackertarget.com/) |
| crt.sh | unlimited | no key — direct PostgreSQL |
| WHOIS | unlimited | no key — asyncwhois |
| Claude API | pay-per-token | [console.anthropic.com](https://console.anthropic.com/) |

---

## License

MIT — build on it, learn from it, get hired with it.
