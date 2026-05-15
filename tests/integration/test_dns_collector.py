import ipaddress

import pytest

from infrastructure.external_apis.dns_collector import DnsCollector


@pytest.mark.asyncio
async def test_fetch_github_has_nonempty_dns_a():
    result = await DnsCollector().fetch("github.com")
    assert "dns_a" in result
    assert len(result["dns_a"]) > 0


@pytest.mark.asyncio
async def test_fetch_github_dns_a_are_valid_ips():
    result = await DnsCollector().fetch("github.com")
    for addr in result["dns_a"]:
        ipaddress.ip_address(addr)  # raises ValueError if not a valid IP
