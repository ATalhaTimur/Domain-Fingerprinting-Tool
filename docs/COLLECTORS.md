# Collectors — Domain-Fingerprinting-Tool

Each collector is an infrastructure adapter implementing the `ICollector` port defined in `core/ports/collector_port.py`. They live in `infrastructure/external_apis/`.

## Rules (all collectors)

1. Implement `async def fetch(self, domain: str) -> dict`
2. **Never raise** — catch all exceptions and return `{"error": str(e)}`
3. Set explicit timeouts — 10s default, 15s for JARM
4. Return raw data only — no analysis, no decisions, just data
5. Prefix return keys with the collector name (`whois_*`, `dns_*`, `jarm_*`) to avoid key collisions on merge

---

## WHOIS — asyncwhois

**Why not python-whois:** python-whois is synchronous. Calling it inside `async def` blocks the event loop for the full duration of the socket connection. Every other coroutine in the gather call stalls.

**asyncwhois** is natively awaitable.

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
                "whois_expires":      str(parsed.get("expires")),
                "whois_emails":       parsed.get("emails", []),
                "whois_name_servers": parsed.get("name_servers", []),
            }
        except Exception as e:
            return {"whois_error": str(e)}
```

**What it finds:**
- Registration date — domain registered yesterday = high risk signal
- Registrar — Namecheap, Porkbun frequently used in phishing ops
- Emails — same email across multiple domains → operator attribution

---

## DNS — dns.asyncresolver

**Why not dnspython sync:** Same event loop blocking issue. `dns.asyncresolver` is the async module inside the same dnspython package — no extra install required.

```python
# infrastructure/external_apis/dns_collector.py
from dns import asyncresolver
from dns.exception import DNSException
from core.ports.collector_port import ICollector

class DnsCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        result = {}
        for rtype in ["A", "MX", "NS", "TXT"]:
            try:
                answers = await asyncresolver.resolve(domain, rtype)
                result[f"dns_{rtype.lower()}"] = [str(r) for r in answers]
            except DNSException:
                result[f"dns_{rtype.lower()}"] = []
        return result
```

**What it finds:**
- A record = real IP (if 104.16.x.x or 172.64.x.x → Cloudflare, real IP is hidden)
- NS record = who manages the nameservers
- TXT record = SPF, DKIM, verification codes

**Cloudflare detection:** If A record falls in Cloudflare IP ranges, V2 AI agent will skip JARM (pointless — you'd fingerprint Cloudflare, not the origin server).

---

## urlscan.io — httpx async

urlscan opens the target page with headless Chromium. Its JSON response already contains Analytics IDs, outbound links, and JavaScript globals. **No scraping needed.** BeautifulSoup cannot reliably extract GA/GTM IDs from modern SPA sites because those codes are injected after JS execution.

```python
# infrastructure/external_apis/urlscan_collector.py
import httpx, asyncio, os
from core.ports.collector_port import ICollector

class UrlscanCollector(ICollector):
    BASE = "https://urlscan.io/api/v1"

    async def fetch(self, domain: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Submit scan
                r = await client.post(
                    f"{self.BASE}/scan/",
                    headers={"API-Key": os.getenv("URLSCAN_API_KEY")},
                    json={"url": f"https://{domain}", "visibility": "public"}
                )
                uuid = r.json()["uuid"]

                # Wait for scan to complete
                await asyncio.sleep(15)

                result = await client.get(f"{self.BASE}/result/{uuid}/")
                data = result.json()

            return {
                "urlscan_ip":            data.get("page", {}).get("ip"),
                "urlscan_analytics_ids": self._extract_analytics(data),
                "urlscan_outbound":      self._extract_outbound(data),
                "urlscan_technologies":  data.get("verdicts", {}).get("overall", {}).get("tags", []),
            }
        except Exception as e:
            return {"urlscan_error": str(e)}

    def _extract_analytics(self, data: dict) -> list[str]:
        ids = []
        for g in data.get("data", {}).get("globals", []):
            val = str(g.get("val", ""))
            if any(val.startswith(p) for p in ("G-", "UA-", "GTM-")):
                ids.append(val)
        return list(set(ids))

    def _extract_outbound(self, data: dict) -> list[str]:
        links = data.get("data", {}).get("links", [])
        return [l.get("href", "") for l in links if l.get("href")]
```

**Rate limit:** 100 scans/day on free tier. Cache shield prevents re-scanning the same domain within 24 hours.

---

## crt.sh — asyncpg (direct PostgreSQL)

crt.sh exposes its Certificate Transparency database via a public PostgreSQL endpoint. Querying it directly with asyncpg is **unlimited and free**. The JSON API at `crt.sh/?q=domain` rate-limits more aggressively.

**Important:** crt.sh finds subdomains that have ever had a TLS certificate issued. It does **not** find IP neighbors — that is HackerTarget's job.

```python
# infrastructure/external_apis/crtsh_collector.py
import asyncpg
from core.ports.collector_port import ICollector

class CrtshCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        try:
            conn = await asyncpg.connect(
                host="crt.sh", port=5432,
                database="certwatch", user="guest",
                timeout=10
            )
            rows = await conn.fetch("""
                SELECT DISTINCT LOWER(NAME_VALUE) AS name
                FROM certificate_and_identities
                WHERE LOWER(NAME_VALUE) LIKE $1
                ORDER BY name LIMIT 200
            """, f"%.{domain.lower()}")
            await conn.close()

            subdomains = [r["name"] for r in rows if r["name"] != domain]
            return {"crtsh_subdomains": subdomains, "crtsh_count": len(subdomains)}
        except Exception as e:
            return {"crtsh_error": str(e), "crtsh_subdomains": []}
```

---

## HackerTarget — httpx async

Finds other domains hosted on the same IP address. Phishing operators frequently run multiple fake sites on a single cheap VPS.

This is the reverse IP lookup. crt.sh cannot do this — crt.sh only sees certificate logs, not IP allocations.

```python
# infrastructure/external_apis/hackertarget_collector.py
import httpx
from core.ports.collector_port import ICollector

class HackerTargetCollector(ICollector):
    async def fetch(self, domain: str, ip: str = "") -> dict:
        if not ip:
            return {"ht_neighbors": [], "ht_note": "no ip provided"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
                )
            if "error" in r.text.lower():
                return {"ht_neighbors": [], "ht_error": r.text}
            neighbors = [l.strip() for l in r.text.splitlines() if l.strip()]
            return {"ht_ip": ip, "ht_neighbors": neighbors}
        except Exception as e:
            return {"ht_error": str(e), "ht_neighbors": []}
```

**Note:** This collector depends on the DNS collector's A record result. In `CollectorService`, DNS runs in the gather batch first, then HackerTarget is called with the resolved IP.

---

## JARM — asyncio.to_thread()

JARM sends 10 custom TLS packets to the target server and derives a 62-character fingerprint from the responses. Identical JARM hash across multiple domains = identical server software = likely same operator.

**python-jarm is synchronous.** Calling it inside `async def` without isolation freezes the event loop — no other coroutine progresses while JARM waits for TCP responses.

`asyncio.to_thread()` offloads the blocking call to a thread pool. The event loop stays free. JARM runs concurrently with the other collectors.

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
            return {"jarm_error": str(e), "jarm_hash": None}
```

**Known malicious JARM hashes** (stored in `infrastructure/external_apis/jarm_c2_list.json`):
```json
{
  "2ad2ad0002ad2ad00042d42d0000002ad2ad": "Cobalt Strike default",
  "07d0d00a7f0a7f57000000000000000000":   "AsyncRAT",
  "29d29d00029d29d00042d43d0000002ad2ad": "Metasploit listener"
}
```

---

## Collector orchestration

In `application/services/collector_service.py`, all collectors fire concurrently:

```python
results = await asyncio.gather(
    whois.fetch(domain),
    dns.fetch(domain),
    urlscan.fetch(domain),
    crtsh.fetch(domain),
    jarm.fetch(domain),
    return_exceptions=True
)
```

`return_exceptions=True` is mandatory. If urlscan.io is down, the other four sources must still complete. A single API failure must never abort the entire scan.

HackerTarget runs after the gather batch because it needs the IP from DNS results:

```python
dns_result = merged.get("dns_a", [None])[0]
if dns_result:
    ht_result = await hackertarget.fetch(domain, ip=dns_result)
    merged.update(ht_result)
```
