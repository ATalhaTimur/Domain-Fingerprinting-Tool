# Deployment — Domain-Fingerprinting-Tool

## Target: zero infrastructure cost

| Component | Platform | Plan |
|-----------|----------|------|
| Backend (FastAPI) | Render.com | Free |
| Frontend (D3.js) | Vercel | Free |
| Cache (dev) | SQLite | Free |
| Cache (prod) | Render Redis | Free |
| CI/CD | GitHub Actions | Free |

---

## Environment variables

```bash
cp .env.example .env
```

See `.env.example` for all required variables. Never commit `.env` to version control.

---

## Local development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Create cache directory (SQLite dev mode)
mkdir -p cache

# Run API
uvicorn api.main:app --reload --port 8000

# Or with Docker
docker compose up
```

---

## Docker

```bash
# Build
docker build -t Domain-Fingerprinting-Tool .

# Run
docker run -p 8000:8000 --env-file .env Domain-Fingerprinting-Tool
```

Multi-stage build keeps the final image lean: builder stage installs dependencies, runtime stage copies only what's needed. Non-root user (`Domain-Fingerprinting-Tool`) runs the process.

---

## Render.com (Backend)

1. Push to GitHub
2. Render → New → Web Service → connect repo
3. Settings:
   - **Runtime:** Python 3.11
   - **Build command:** `pip install -e .`
   - **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`
5. Deploy

Free tier: 750 hours/month. Sleeps after 15 minutes of inactivity (first request ~30s cold start). Acceptable for V1.

---

## Vercel (Frontend)

```bash
npm i -g vercel
cd frontend
vercel deploy
```

Or connect GitHub repo to Vercel, set `frontend/` as root directory. Auto-deploys on every push.

---

## GitHub Actions (CI)

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit -v
```

Unit tests run on every push. Integration tests (which hit real APIs) are excluded from CI — run them manually.

---

## Production checklist

- [ ] All API keys set as environment variables (never hardcoded)
- [ ] `APP_ENV=production` set
- [ ] `CACHE_BACKEND=redis` set
- [ ] CORS restricted to frontend domain only
- [ ] `/api/v1/scan` validates domain format before processing
- [ ] Error responses do not expose stack traces
- [ ] Rate limiting middleware active (FastAPI SlowAPI)
- [ ] Docker image uses non-root user
