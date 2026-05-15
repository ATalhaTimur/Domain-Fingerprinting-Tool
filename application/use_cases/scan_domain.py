import uuid

from application.dto.scan_request import ScanRequestDTO
from application.dto.scan_response import ScanResponseDTO
from application.services.analyzer_service import AnalyzerService
from application.services.collector_service import CollectorService
from application.services.data_prepper import DataPrepper
from core.domain.entities.domain_target import DomainTarget
from core.domain.entities.scan import Scan
from core.ports.ai_port import IAIAnalyzer
from core.ports.cache_port import ICache
from core.ports.graph_port import IGraphBuilder


class ScanDomainUseCase:
    def __init__(
        self,
        cache:         ICache,
        collector_svc: CollectorService,
        analyzer_svc:  AnalyzerService,
        graph_builder: IGraphBuilder,
        data_prepper:  DataPrepper,
        ai_analyzer:   IAIAnalyzer,
    ):
        self._cache         = cache
        self._collector_svc = collector_svc
        self._analyzer_svc  = analyzer_svc
        self._graph_builder = graph_builder
        self._data_prepper  = data_prepper
        self._ai_analyzer   = ai_analyzer

    async def execute(self, request: ScanRequestDTO) -> ScanResponseDTO:
        target = DomainTarget.from_url(request.target)

        # 1. Cache shield
        cached = await self._cache.get(target.value)
        if cached:
            return ScanResponseDTO.from_cache(cached)

        # 2. Collect
        raw = await self._collector_svc.collect_all(target.value)

        # 3. Analyze
        analysis = self._analyzer_svc.analyze(raw)

        # 4. Build graph  (domain key required by NetworkXGraphBuilder)
        graph = self._graph_builder.build({"domain": target.value, **raw, **analysis})

        # 5. Prepare for AI
        relations_text = self._data_prepper.prepare(graph, analysis)

        # 6. AI summary
        summary = await self._ai_analyzer.analyze(relations_text, request.mode)

        # 7. Build scan entity
        scan = Scan(id=str(uuid.uuid4()), target=target)
        scan.complete(raw, analysis["risk_score"])

        # 8. Cache result
        result = ScanResponseDTO(scan=scan, graph=graph, summary=summary)
        await self._cache.set(target.value, result.to_dict(), ttl_seconds=86400)

        return result
