import pytest
from infrastructure.external_apis.whois_collector import WhoisCollector


@pytest.mark.asyncio
async def test_fetch_real_domain_returns_registrar():
    result = await WhoisCollector().fetch("github.com")
    assert "whois_error" not in result
    assert "whois_registrar" in result
    assert result["whois_registrar"] is not None


@pytest.mark.asyncio
async def test_fetch_invalid_domain_returns_error_key():
    result = await WhoisCollector().fetch("thisisnotavaliddomain12345.xyz")
    assert "whois_error" in result
