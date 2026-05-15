import json
from datetime import datetime, timezone
from pathlib import Path

from core.domain.entities.risk_score import RiskScore

_C2_LIST_PATH = Path(__file__).parent.parent.parent / "infrastructure" / "external_apis" / "jarm_c2_list.json"

with _C2_LIST_PATH.open() as _f:
    _JARM_C2: dict[str, str] = json.load(_f)


def _parse_domain_age(whois_created: str | None) -> int | None:
    if not whois_created or whois_created == "None":
        return None
    try:
        created = datetime.fromisoformat(whois_created)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - created).days
    except (ValueError, TypeError):
        return None


class AnalyzerService:
    def analyze(self, raw: dict) -> dict:
        jarm_c2_match   = _JARM_C2.get(raw.get("jarm_hash") or "")
        analytics_ids   = raw.get("urlscan_analytics_ids") or []
        domain_age_days = _parse_domain_age(raw.get("whois_created"))
        has_neighbors   = bool(raw.get("ht_neighbors"))

        score = 0
        if jarm_c2_match:
            score += 40
        if has_neighbors:
            score += 30
        if domain_age_days is not None and domain_age_days < 7:
            score += 20
        if analytics_ids:
            score += 10

        return {
            "jarm_c2_match":     jarm_c2_match,
            "analytics_overlap": analytics_ids,
            "ip_correlation": {
                "subdomains": raw.get("crtsh_subdomains", []),
                "neighbors":  raw.get("ht_neighbors", []),
            },
            "domain_age_days": domain_age_days,
            "risk_score":      RiskScore(min(score, 100)),
        }
