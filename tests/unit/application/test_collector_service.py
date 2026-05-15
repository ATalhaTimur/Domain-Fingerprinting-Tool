import pytest
from unittest.mock import AsyncMock

from application.services.collector_service import CollectorService


def _make_service(*fetch_results, ht_result=None):
    """Build a CollectorService with mocked collectors and HackerTarget."""
    collectors = []
    for result in fetch_results:
        mock = AsyncMock()
        if isinstance(result, Exception):
            mock.fetch.side_effect = result
        else:
            mock.fetch.return_value = result
        collectors.append(mock)

    hackertarget = AsyncMock()
    hackertarget.fetch.return_value = ht_result or {}

    return CollectorService(collectors=collectors, hackertarget=hackertarget)


@pytest.mark.asyncio
async def test_collect_all_merges_results():
    svc = _make_service({"a": 1}, {"b": 2})
    result = await svc.collect_all("example.com")
    assert result == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_collect_all_skips_exceptions():
    svc = _make_service(Exception("network error"), {"b": 2})
    result = await svc.collect_all("example.com")
    assert "b" in result
    assert result["b"] == 2


@pytest.mark.asyncio
async def test_collect_all_exception_does_not_drop_other_results():
    svc = _make_service({"a": 1}, Exception("timeout"), {"c": 3})
    result = await svc.collect_all("example.com")
    assert result.get("a") == 1
    assert result.get("c") == 3
    assert "b" not in result


@pytest.mark.asyncio
async def test_collect_all_calls_hackertarget_when_dns_a_present():
    svc = _make_service(
        {"dns_a": ["1.2.3.4"], "dns_ns": []},
        ht_result={"ht_ip": "1.2.3.4", "ht_neighbors": ["evil.com"]},
    )
    result = await svc.collect_all("example.com")
    assert result.get("ht_ip") == "1.2.3.4"
    assert "evil.com" in result.get("ht_neighbors", [])
    svc._hackertarget.fetch.assert_awaited_once_with("example.com", ip="1.2.3.4")


@pytest.mark.asyncio
async def test_collect_all_skips_hackertarget_when_no_dns_a():
    svc = _make_service({"whois_registrar": "GoDaddy"})
    result = await svc.collect_all("example.com")
    svc._hackertarget.fetch.assert_not_awaited()
    assert "whois_registrar" in result
