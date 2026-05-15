# Contributing — Domain-Fingerprinting-Tool

## Setup

```bash
git clone https://github.com/ATalhaTimur/Domain-Fingerprinting-Tool
cd Domain-Fingerprinting-Tool
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

---

## Adding a new collector

1. Create `infrastructure/external_apis/your_collector.py`
2. Implement `ICollector` from `core/ports/collector_port.py`
3. Follow the contract: `async def fetch(self, domain: str) -> dict`
4. Catch all exceptions — return `{"your_prefix_error": str(e)}`
5. Prefix all return keys with the collector name to avoid merge collisions
6. Register it in `api/main.py` inside `create_app()`
7. Document it in `docs/COLLECTORS.md`

Minimum template:

```python
from core.ports.collector_port import ICollector

class YourCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        try:
            # ... fetch data ...
            return {"your_prefix_key": value}
        except Exception as e:
            return {"your_prefix_error": str(e)}
```

---

## Code standards

- **Async everywhere** — sync I/O is forbidden; use `asyncio.to_thread()` for blocking libs
- **Type hints required** — all function signatures must be typed
- **One responsibility per class** — collectors fetch, analyzers analyze, use cases orchestrate
- **No magic numbers** — constants go in `core/domain/` or config
- **No business logic in `api/`** — routes call use cases, nothing else

---

## Testing

```bash
# Unit tests only (fast, no network)
pytest tests/unit -v

# All tests including integration (needs real API keys)
pytest tests/ -v

# With coverage
pytest tests/unit --cov=. --cov-report=term-missing
```

Unit tests in `tests/unit/` require no mocking for `core/` and `application/` — those layers are pure functions. Infrastructure tests in `tests/integration/` hit real external services and require valid API keys.

---

## V2 compatibility

Every collector you write in V1 will become a LangGraph tool in V2. Keep this in mind:

- Function signatures should be clean and self-describing
- The `domain` parameter must remain the primary input
- Return dicts should be flat — no deeply nested structures
- No side effects — fetch, return, done

V2 migration will wrap each collector with a `@tool` decorator. If the collector is clean, the wrapper is 3 lines.
