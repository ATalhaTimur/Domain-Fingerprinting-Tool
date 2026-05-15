from datetime import datetime, timedelta, timezone

import pytest

from application.services.analyzer_service import AnalyzerService
from core.domain.entities.risk_score import RiskScore

svc = AnalyzerService()

COBALT_STRIKE_HASH = "2ad2ad0002ad2ad00042d42d0000002ad2ad"


def test_jarm_match_returns_correct_c2_name():
    result = svc.analyze({"jarm_hash": COBALT_STRIKE_HASH})
    assert result["jarm_c2_match"] == "Cobalt Strike default"


def test_jarm_no_match_returns_none():
    result = svc.analyze({"jarm_hash": "0000000000000000000000000000000000"})
    assert result["jarm_c2_match"] is None


def test_risk_score_caps_at_100():
    # all four signals fire: jarm(+40) + neighbors(+30) + new domain(+20) + analytics(+10) = 100
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    result = svc.analyze({
        "jarm_hash":              COBALT_STRIKE_HASH,
        "ht_neighbors":           ["bad.com"],
        "whois_created":          yesterday,
        "urlscan_analytics_ids":  ["G-XXXXXXXXXX"],
    })
    assert result["risk_score"] == RiskScore(100)


def test_empty_raw_returns_risk_score_zero():
    result = svc.analyze({})
    assert result["risk_score"] == RiskScore(0)


def test_domain_age_under_7_days_adds_score():
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    result = svc.analyze({"whois_created": yesterday})
    assert result["risk_score"].value == 20
    assert result["domain_age_days"] == 1


def test_domain_age_over_7_days_no_score():
    old = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
    result = svc.analyze({"whois_created": old})
    assert result["risk_score"].value == 0


def test_analytics_overlap_populates_and_scores():
    result = svc.analyze({"urlscan_analytics_ids": ["G-ABC123", "GTM-XYZ"]})
    assert result["analytics_overlap"] == ["G-ABC123", "GTM-XYZ"]
    assert result["risk_score"].value == 10


def test_ip_correlation_links_subdomains_and_neighbors():
    result = svc.analyze({
        "crtsh_subdomains": ["api.example.com", "www.example.com"],
        "ht_neighbors":     ["evil.com"],
    })
    assert result["ip_correlation"]["subdomains"] == ["api.example.com", "www.example.com"]
    assert result["ip_correlation"]["neighbors"] == ["evil.com"]


def test_missing_jarm_hash_does_not_raise():
    result = svc.analyze({"dns_a": ["1.2.3.4"]})
    assert result["jarm_c2_match"] is None
    assert result["risk_score"] == RiskScore(0)
