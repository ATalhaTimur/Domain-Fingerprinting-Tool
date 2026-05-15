# Architecture — Domain-Fingerprinting-Tool

## Design philosophy

Domain-Fingerprinting-Tool follows **Clean Architecture** with **Domain-Driven Design** layering. If you come from .NET, think of it as the Python equivalent of the onion architecture you know from ASP.NET Core.

The fundamental rule: **dependencies point inward only**.

```
         ┌─────────────────────────────────┐
         │           api / cli             │  ← delivery mechanisms
         │  ┌───────────────────────────┐  │
         │  │      infrastructure       │  │  ← frameworks, I/O, DB
         │  │  ┌─────────────────────┐  │  │
         │  │  │     application     │  │  │  ← use cases, orchestration
         │  │  │  ┌───────────────┐  │  │  │
         │  │  │  │     core      │  │  │  │  ← domain entities, ports
         │  │  │  └───────────────┘  │  │  │
         │  │  └─────────────────────┘  │  │
         │  └───────────────────────────┘  │
         └─────────────────────────────────┘
```

`core` knows nothing about FastAPI, Redis, or httpx. `infrastructure` implements the interfaces `core` defines. `application` orchestrates without touching I/O directly. `api` and `cli` are just delivery wires.

---

## Layer breakdown

### core/ — Enterprise business rules

The innermost layer. Zero external dependencies. If this layer changes, something fundamental about the domain has changed.

#### core/domain/entities/

**`Scan`** — aggregate root. Represents one complete scan lifecycle.

```python
# core/domain/entities/scan.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from core.domain.entities.domain_target import DomainTarget
from core.domain.entities.risk_score import RiskScore

class ScanStatus(Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"

@dataclass
class Scan:
    id:           str
    target:       DomainTarget
    status:       ScanStatus = ScanStatus.PENDING
    risk_score:   RiskScore  = field(default_factory=RiskScore.zero)
    raw_data:     dict       = field(default_factory=dict)
    created_at:   datetime   = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def complete(self, raw_data: dict, risk_score: RiskScore) -> None:
        self.raw_data     = raw_data
        self.risk_score   = risk_score
        self.status       = ScanStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail(self, reason: str) -> None:
        self.status = ScanStatus.FAILED
        self.raw_data["failure_reason"] = reason
```

**`DomainTarget`** — value object. Immutable, self-validating.

```python
# core/domain/entities/domain_target.py
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class DomainTarget:
    value: str

    def __post_init__(self) -> None:
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid domain: {self.value}")

    @classmethod
    def from_url(cls, raw: str) -> "DomainTarget":
        # strip scheme, path, query
        import re
        domain = re.sub(r'^https?://', '', raw).split('/')[0].split('?')[0]
        return cls(domain)
```

**`RiskScore`** — value object. Bounded 0–100.

```python
# core/domain/entities/risk_score.py
from dataclasses import dataclass

@dataclass(frozen=True)
class RiskScore:
    value: int

    def __post_init__(self) -> None:
        if not (0 <= self.value <= 100):
            raise ValueError(f"RiskScore must be 0–100, got {self.value}")

    @classmethod
    def zero(cls) -> "RiskScore":
        return cls(0)

    @property
    def level(self) -> str:
        if self.value >= 70: return "critical"
        if self.value >= 40: return "medium"
        return "low"
```

**`ThreatGraph`** — entity. Holds the network of relationships discovered.

```python
# core/domain/entities/threat_graph.py
from dataclasses import dataclass, field

@dataclass
class ThreatNode:
    id:       str
    type:     str          # domain | ip | analytics_id | jarm_hash
    metadata: dict = field(default_factory=dict)

@dataclass
class ThreatEdge:
    source:   str
    target:   str
    relation: str          # resolves_to | ip_neighbor | analytics_shared | c2_match

@dataclass
class ThreatGraph:
    nodes: list[ThreatNode] = field(default_factory=list)
    edges: list[ThreatEdge] = field(default_factory=list)

    def add_node(self, node: ThreatNode) -> None:
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)

    def add_edge(self, edge: ThreatEdge) -> None:
        self.edges.append(edge)
```

#### core/ports/ — Abstract interfaces (contracts)

Ports are the contracts that infrastructure must fulfill. This is the Ports & Adapters pattern — identical to `IRepository` interfaces in .NET.

```python
# core/ports/collector_port.py
from abc import ABC, abstractmethod

class ICollector(ABC):
    @abstractmethod
    async def fetch(self, domain: str) -> dict:
        """Fetch raw data for a domain. Never raises — returns {"error": ...} on failure."""
        ...

# core/ports/cache_port.py
class ICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> dict | None: ...

    @abstractmethod
    async def set(self, key: str, value: dict, ttl_seconds: int) -> None: ...

# core/ports/ai_port.py
class IAIAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, relations_text: str, mode: str) -> str: ...

# core/ports/graph_port.py
from core.domain.entities.threat_graph import ThreatGraph

class IGraphBuilder(ABC):
    @abstractmethod
    def build(self, raw_data: dict) -> ThreatGraph: ...
```

---

### application/ — Use cases and orchestration

Application layer knows the ports but not the implementations. It calls `ICollector.fetch()`, not `WhoisCollector.fetch()`. Concrete classes are injected at startup (dependency injection).

#### application/use_cases/scan_domain.py

```python
from core.ports.cache_port      import ICache
from core.ports.collector_port  import ICollector
from core.ports.ai_port         import IAIAnalyzer
from core.ports.graph_port      import IGraphBuilder
from application.services.collector_service import CollectorService
from application.services.analyzer_service  import AnalyzerService
from application.services.data_prepper      import DataPrepper
from application.dto.scan_request  import ScanRequestDTO
from application.dto.scan_response import ScanResponseDTO
from core.domain.entities.domain_target import DomainTarget
from core.domain.entities.scan import Scan
import uuid

class ScanDomainUseCase:
    def __init__(
        self,
        cache:           ICache,
        collector_svc:   CollectorService,
        analyzer_svc:    AnalyzerService,
        graph_builder:   IGraphBuilder,
        data_prepper:    DataPrepper,
        ai_analyzer:     IAIAnalyzer,
    ):
        self._cache         = cache
        self._collector_svc = collector_svc
        self._analyzer_svc  = analyzer_svc
        self._graph_builder = graph_builder
        self._data_prepper  = data_prepper
        self._ai_analyzer   = ai_analyzer

    async def execute(self, request: ScanRequestDTO) -> ScanResponseDTO:
        target = DomainTarget.from_url(request.target)

        # 1. Cache shield
        cached = await self._cache.get(target.value)
        if cached:
            return ScanResponseDTO.from_cache(cached)

        # 2. Collect
        raw = await self._collector_svc.collect_all(target.value)

        # 3. Analyze
        analysis = self._analyzer_svc.analyze(raw)

        # 4. Build graph
        graph = self._graph_builder.build({**raw, **analysis})

        # 5. Prepare for AI
        relations_text = self._data_prepper.prepare(graph, analysis)

        # 6. AI summary
        summary = await self._ai_analyzer.analyze(relations_text, request.mode)

        # 7. Build scan entity
        scan = Scan(id=str(uuid.uuid4()), target=target)
        scan.complete(raw, analysis["risk_score"])

        # 8. Cache result
        result = ScanResponseDTO(scan=scan, graph=graph, summary=summary)
        await self._cache.set(target.value, result.to_dict(), ttl_seconds=86400)

        return result
```

#### application/services/collector_service.py

```python
import asyncio
from core.ports.collector_port import ICollector

class CollectorService:
    def __init__(self, collectors: list[ICollector]):
        self._collectors = collectors

    async def collect_all(self, domain: str) -> dict:
        results = await asyncio.gather(
            *[c.fetch(domain) for c in self._collectors],
            return_exceptions=True   # one failure must not kill the rest
        )
        merged = {}
        for r in results:
            if isinstance(r, Exception):
                continue
            merged.update(r)
        return merged
```

#### application/services/data_prepper.py

```python
from core.domain.entities.threat_graph import ThreatGraph

class DataPrepper:
    """
    Strips visual metadata (x/y coords, colors, sizes) from the graph.
    Produces a compact relational text for the LLM.
    Coordinates and hex colors cost tokens with zero intelligence value.
    """

    def prepare(self, graph: ThreatGraph, analysis: dict) -> str:
        lines = [
            f"{e.source} → {e.target} [{e.relation}]"
            for e in graph.edges
        ]
        lines.append(f"overall_risk_score: {analysis.get('risk_score', 0)}/100")

        if analysis.get("jarm_c2_match"):
            lines.append(f"jarm_c2_match: {analysis['jarm_c2_match']}")
        if analysis.get("domain_age_days") is not None:
            lines.append(f"domain_age_days: {analysis['domain_age_days']}")

        return "\n".join(lines)
```

---

### infrastructure/ — Frameworks and drivers

Infrastructure implements the ports defined in `core`. Each class is an adapter.

#### infrastructure/cache/

```
sqlite_cache.py   →  ICache  (dev — aiosqlite)
redis_cache.py    →  ICache  (prod — redis-py async)
```

Same interface, swapped at startup via environment variable. Application layer never knows which one is running.

#### infrastructure/ai/claude_analyzer.py

```python
import httpx, os
from core.ports.ai_port import IAIAnalyzer
from infrastructure.ai.prompts import PROMPTS

class ClaudeAnalyzer(IAIAnalyzer):
    MODEL = "claude-sonnet-4-6"

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
                    "system":     PROMPTS[mode],
                    "messages": [{
                        "role":    "user",
                        "content": f"Analyze the following infrastructure relationships:\n\n{relations_text}"
                    }]
                }
            )
        return r.json()["content"][0]["text"]
```

#### infrastructure/external_apis/

Every collector is an adapter implementing `ICollector`:

```python
# infrastructure/external_apis/whois_collector.py
import asyncwhois
from core.ports.collector_port import ICollector

class WhoisCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        try:
            _, parsed = await asyncwhois.aio_whois(domain)
            return {
                "whois_registrar":    parsed.get("registrar"),
                "whois_created":      str(parsed.get("created")),
                "whois_emails":       parsed.get("emails", []),
                "whois_name_servers": parsed.get("name_servers", []),
            }
        except Exception as e:
            return {"whois_error": str(e)}
```

JARM collector uses `asyncio.to_thread()` because `python-jarm` is synchronous:

```python
# infrastructure/external_apis/jarm_collector.py
import asyncio
from jarm.scanner.scanner import Scanner
from core.ports.collector_port import ICollector

class JarmCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        try:
            jarm_hash = await asyncio.to_thread(Scanner.scan, domain, 443)
            return {"jarm_hash": jarm_hash}
        except Exception as e:
            return {"jarm_error": str(e)}
```

---

### api/ — Delivery mechanism

FastAPI is just a delivery wire. It calls use cases, nothing else.

```python
# api/routes/scan.py
from fastapi import APIRouter, Request
from application.dto.scan_request import ScanRequestDTO

router = APIRouter(prefix="/api/v1")

@router.post("/scan")
async def scan(body: ScanRequestDTO, request: Request):
    use_case = request.app.state.scan_use_case
    result = await use_case.execute(body)
    return result.to_dict()   # .to_dict() required — RiskScore is a dataclass
```

Routes do not contain business logic. They validate input, call a use case, return the result. `to_dict()` is called explicitly so FastAPI serializes `RiskScore` as a plain integer rather than `{"value": N}`.

---

### Dependency injection

All wiring happens in `api/main.py`. This is the composition root — equivalent to `Program.cs` in .NET.

```python
# api/main.py
from fastapi import FastAPI
from infrastructure.cache.sqlite_cache    import SqliteCache
from infrastructure.cache.redis_cache     import RedisCache
from infrastructure.ai.claude_analyzer    import ClaudeAnalyzer
from infrastructure.external_apis.whois_collector      import WhoisCollector
from infrastructure.external_apis.dns_collector        import DnsCollector
from infrastructure.external_apis.urlscan_collector    import UrlscanCollector
from infrastructure.external_apis.crtsh_collector      import CrtshCollector
from infrastructure.external_apis.hackertarget_collector import HackerTargetCollector
from infrastructure.external_apis.jarm_collector       import JarmCollector
from infrastructure.external_apis.networkx_graph       import NetworkXGraphBuilder
from application.use_cases.scan_domain   import ScanDomainUseCase
from application.services.collector_service import CollectorService
from application.services.analyzer_service  import AnalyzerService
from application.services.data_prepper      import DataPrepper
import os

def create_app() -> FastAPI:
    app = FastAPI(title="Domain-Fingerprinting-Tool")

    cache = RedisCache() if os.getenv("APP_ENV") == "production" else SqliteCache()

    collectors = [
        WhoisCollector(),
        DnsCollector(),
        UrlscanCollector(),
        CrtshCollector(),
        HackerTargetCollector(),
        JarmCollector(),
    ]

    use_case = ScanDomainUseCase(
        cache=cache,
        collector_svc=CollectorService(collectors),
        analyzer_svc=AnalyzerService(),
        graph_builder=NetworkXGraphBuilder(),
        data_prepper=DataPrepper(),
        ai_analyzer=ClaudeAnalyzer(),
    )

    app.state.scan_use_case = use_case
    return app

app = create_app()
```

---

## Testing strategy

```
tests/
├── unit/          # test domain logic and application services in isolation
│   ├── core/      # RiskScore bounds, DomainTarget validation, ThreatGraph logic
│   └── application/  # AnalyzerService, DataPrepper — pure functions, no mocks needed
│
├── integration/   # test infrastructure adapters against real external services
│   ├── test_whois_collector.py     # hits real asyncwhois
│   └── test_crtsh_collector.py     # hits real crt.sh PostgreSQL
│
└── e2e/           # test full use case flow with mocked infrastructure
    └── test_scan_domain.py
```

Unit tests for `core` and `application` need zero mocking — they are pure functions. Integration tests for `infrastructure` need real network access. E2E tests wire the full use case with mocked collectors.

---

## V1 → V2 migration path

V1 collectors are `ICollector` adapters. In V2, they become LangGraph tools:

```python
# V2: same WhoisCollector, new wrapper
from langgraph.prebuilt import create_react_agent

tools = [c.as_tool() for c in collectors]   # thin wrapper, no refactor
agent = create_react_agent(model, tools)
```

Clean Architecture pays off here. Because `infrastructure` is isolated behind ports, swapping the orchestration layer from `asyncio.gather` to LangGraph requires no changes to domain logic, application services, or collector implementations.
