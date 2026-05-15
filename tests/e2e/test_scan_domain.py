import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.scan_request import ScanRequestDTO
from application.dto.scan_response import ScanResponseDTO
from application.use_cases.scan_domain import ScanDomainUseCase
from core.domain.entities.domain_target import DomainTarget
from core.domain.entities.risk_score import RiskScore
from core.domain.entities.scan import Scan
from core.domain.entities.threat_graph import ThreatGraph


def _analysis():
    return {
        "risk_score":      RiskScore(30),
        "jarm_c2_match":   None,
        "analytics_overlap": [],
        "domain_age_days": None,
        "ip_correlation":  {"subdomains": [], "neighbors": []},
    }


def _make_use_case(cache_hit=None):
    cache = AsyncMock()
    cache.get.return_value = cache_hit

    collector_svc = AsyncMock()
    collector_svc.collect_all.return_value = {"dns_a": ["1.2.3.4"]}

    analyzer_svc = MagicMock()
    analyzer_svc.analyze.return_value = _analysis()

    graph_builder = MagicMock()
    graph_builder.build.return_value = ThreatGraph()

    data_prepper = MagicMock()
    data_prepper.prepare.return_value = "example.com → 1.2.3.4 [resolves_to]\noverall_risk_score: 30/100"

    ai_analyzer = AsyncMock()
    ai_analyzer.analyze.return_value = "Moderate risk signals detected."

    use_case = ScanDomainUseCase(
        cache=cache,
        collector_svc=collector_svc,
        analyzer_svc=analyzer_svc,
        graph_builder=graph_builder,
        data_prepper=data_prepper,
        ai_analyzer=ai_analyzer,
    )
    return use_case, cache, collector_svc, ai_analyzer


@pytest.mark.asyncio
async def test_execute_checks_cache_first():
    use_case, cache, *_ = _make_use_case()
    await use_case.execute(ScanRequestDTO(target="example.com"))
    cache.get.assert_awaited_once_with("example.com")


@pytest.mark.asyncio
async def test_execute_returns_scan_response_dto_with_summary():
    use_case, *_ = _make_use_case()
    result = await use_case.execute(ScanRequestDTO(target="https://example.com/path?q=1"))
    assert isinstance(result, ScanResponseDTO)
    assert result.summary == "Moderate risk signals detected."


@pytest.mark.asyncio
async def test_execute_calls_cache_set_at_end():
    use_case, cache, *_ = _make_use_case()
    await use_case.execute(ScanRequestDTO(target="example.com"))
    cache.set.assert_awaited_once()
    args, kwargs = cache.set.call_args
    ttl = kwargs.get("ttl_seconds", args[2] if len(args) > 2 else None)
    assert ttl == 86400


@pytest.mark.asyncio
async def test_execute_returns_from_cache_on_hit():
    scan = Scan(id="cached-id", target=DomainTarget("example.com"))
    scan.complete({"dns": "ok"}, RiskScore(10))
    cached_dto = ScanResponseDTO(scan=scan, graph=ThreatGraph(), summary="cached summary")

    use_case, cache, collector_svc, _ = _make_use_case(cache_hit=cached_dto.to_dict())
    result = await use_case.execute(ScanRequestDTO(target="example.com"))

    assert result.summary == "cached summary"
    collector_svc.collect_all.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_strips_url_scheme_and_path():
    use_case, cache, *_ = _make_use_case()
    await use_case.execute(ScanRequestDTO(target="https://github.com/owner/repo?ref=main"))
    cache.get.assert_awaited_once_with("github.com")


@pytest.mark.asyncio
async def test_execute_scan_entity_status_is_completed():
    use_case, *_ = _make_use_case()
    result = await use_case.execute(ScanRequestDTO(target="example.com"))
    from core.domain.entities.scan import ScanStatus
    assert result.scan.status == ScanStatus.COMPLETED
