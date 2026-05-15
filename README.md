<div align="center">

# Domain Fingerprinting Tool

**One signal in. The whole adversarial network out.**

[![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-10b981?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.x-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Claude AI](https://img.shields.io/badge/Claude-Sonnet_4-8b5cf6?style=flat-square)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](LICENSE)

</div>

---

## What is this?

Most threat intelligence tools stop at the artifact — the domain, the IP, the hash. DFT goes further.

Give it a single domain. It traces the infrastructure behind it: shared IPs, overlapping TLS fingerprints, re-used analytics IDs, subdomain clusters. It builds a **visual graph** of the entire network and asks Claude to explain what it means in plain language.

The difference between cutting a branch and pulling the root.

---

## Demo

---

## How it works

```
Input  ──────────────────────────────────────────────────────────────
  domain / URL / IP
        │
        ▼
Cache Shield  ───────────────────────────────── HIT → skip to Output
  SQLite (dev)  /  Redis (prod)
        │ MISS
        ▼
Collector Layer  (parallel — asyncio.gather) ───────────────────────
  ├── WHOIS          registrar, creation date, name servers
  ├── DNS            A / MX / NS / TXT records
  ├── urlscan.io     screenshot, analytics IDs, linked domains
  ├── crt.sh         TLS certificate history, subdomain clusters
  ├── HackerTarget   IP neighbors on same /24 block
  └── JARM           TLS stack fingerprint → C2 signature match
        │
        ▼
Analyzer Layer  (zero I/O — pure domain logic) ─────────────────────
  ├── Analytics overlap   same GA / GTM tag → same operator
  ├── IP correlation      neighbor clustering + subdomain linking
  └── JARM scoring        hash vs known C2 list → risk score 0–100
        │
        ▼
Graph Builder  (NetworkX) ──────────────────────────────────────────
  nodes: domain / ip / analytics_id / jarm_hash / subdomain
  edges: resolves_to / ip_neighbor / analytics_shared / c2_match
        │
        ▼
AI Analyzer  (Claude API) ──────────────────────────────────────────
  ├── Technical mode   →  senior threat analyst tone
  └── Executive mode   →  CISO briefing tone
        │
        ▼
Output ─────────────────────────────────────────────────────────────
  ├── Interactive graph   Vue 3 + D3.js  (force-directed, zoomable)
  ├── REST API            FastAPI        POST /api/v1/scan
  └── CLI                 typer          python -m cli.commands scan
```

---

## Features

| Feature | What it does |
|---|---|
| **Parallel collection** | All 6 collectors run concurrently via `asyncio.gather()` — no sequential waits |
| **Cache shield** | Results cached 24h. API rate limits never wasted on duplicate domains |
| **JARM fingerprinting** | Identifies TLS stack: Cloudflare, bare Nginx, or known C2 malware signatures |
| **crt.sh via PostgreSQL** | Direct DB connection to crt.sh — unlimited, no API key, no rate limit |
| **Analytics ID overlap** | Same Google Analytics / GTM tag across different domains = same operator |
| **Risk scoring** | 0–100 score from JARM C2 match, domain age, analytics overlap, and IP clustering |
| **AI dual-mode** | Technical analyst depth or executive CISO brevity — same data, different lens |
| **Force-directed graph** | Interactive D3.js visualization — click nodes, inspect metadata, zoom/pan |
| **Side panel** | Node inspector, full node list, AI analysis — tab-based, zero layout shift |
| **Zero infra cost** | Render.com backend + Vercel frontend, both free tier |

---

## Tech stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, asyncio |
| **Frontend** | Vue 3 (Composition API), Vite, D3.js v7 |
| **Graph engine** | NetworkX |
| **AI** | Anthropic Claude (claude-sonnet-4-6) |
| **Cache** | SQLite (dev), Redis (prod) |
| **Collectors** | asyncwhois, dns.asyncresolver, httpx, asyncpg, python-jarm |
| **Architecture** | Clean Architecture + DDD (ports & adapters) |

---

## Quick start

**1. Clone and install**

```bash
git clone https://github.com/ATalhaTimur/Domain-Fingerprinting-Tool
cd Domain-Fingerprinting-Tool
pip install -e ".[dev]"
cp .env.example .env       # fill in your API keys
```

**2. Start the backend**

```bash
uvicorn api.main:app --reload --port 8000
```

**3. Start the frontend**

```bash
cd frontend
npm install
npm run dev                # → http://localhost:3000
```

**Or with Docker**

```bash
docker compose up
```

**Or CLI only (no browser)**

```bash
python -m cli.commands scan github.com --mode technical
python -m cli.commands scan github.com --mode executive
```

---

## API keys

| Service | Free tier | Notes |
|---|---|---|
| [urlscan.io](https://urlscan.io/user/signup/) | 100 scans/day | Analytics IDs, screenshots |
| [HackerTarget](https://hackertarget.com/) | ~100 req/day | IP neighbor discovery |
| [Claude API](https://console.anthropic.com/) | Pay-per-token | AI analysis (cheap — ~512 tokens/scan) |
| crt.sh | Unlimited | No key needed — direct PostgreSQL |
| WHOIS | Unlimited | No key needed — asyncwhois |

---

## Architecture

Clean Architecture with DDD layering. Dependencies point inward — `core` knows nothing about FastAPI, Redis, or httpx.

```
api / cli                 ← delivery mechanisms
  └── infrastructure      ← frameworks, I/O, external APIs
        └── application   ← use cases, orchestration
              └── core    ← domain entities, ports (interfaces)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full layer breakdown, entity definitions, and dependency injection wiring.

```
Domain-Fingerprinting-Tool/
├── core/                          # Enterprise rules — zero dependencies
│   ├── domain/entities/           # Scan, DomainTarget, ThreatGraph, RiskScore
│   └── ports/                     # ICollector, ICache, IAIAnalyzer, IGraphBuilder
├── application/                   # Use cases + services + DTOs
├── infrastructure/                # Adapters: collectors, cache, Claude, NetworkX
├── api/                           # FastAPI routes + middleware
├── cli/                           # typer CLI
├── frontend/                      # Vue 3 + Vite SPA
│   └── src/
│       ├── composables/useScan.js # All scan state + API logic
│       └── components/            # AppHeader, ScanToolbar, GraphView, SidePanel/*
├── tests/                         # unit / integration / e2e
└── docs/                          # ARCHITECTURE, COLLECTORS, AI_LAYER, DEPLOYMENT
```

---

## Roadmap

| | Version | Description |
|---|---|---|
| ✅ | **V1 — Pipeline** | Static parallel collection. All collectors fire at once, AI summarizes at the end. |
| 🔜 | **V2 — Agentic** | LangGraph orchestrates collectors as tools. AI decides what to query and when. If it sees Cloudflare on DNS it skips JARM and jumps straight to analytics overlap. V1 collectors become LangGraph tools with zero refactor. |

---

## License

MIT — build on it, learn from it, ship it.
