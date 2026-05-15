import pytest

from infrastructure.external_apis.crtsh_collector import CrtshCollector


@pytest.mark.asyncio
async def test_fetch_github_returns_subdomains():
    result = await CrtshCollector().fetch("github.com")
    if "crtsh_error" in result:
        # crt.sh imposes server-side statement timeouts on high-volume domains;
        # treat as a skip rather than a failure so CI stays green on flaky days
        pytest.skip(f"crt.sh server error (external): {result['crtsh_error']}")
    assert "crtsh_subdomains" in result
    assert len(result["crtsh_subdomains"]) > 0


@pytest.mark.asyncio
async def test_fetch_github_count_matches_list():
    result = await CrtshCollector().fetch("github.com")
    if "crtsh_error" not in result:
        assert result["crtsh_count"] == len(result["crtsh_subdomains"])
