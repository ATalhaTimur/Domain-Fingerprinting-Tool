import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from application.services.analyzer_service import AnalyzerService
from application.services.collector_service import CollectorService
from application.services.data_prepper import DataPrepper
from application.use_cases.scan_domain import ScanDomainUseCase
from api.middleware.error_handler import ErrorHandlerMiddleware
from api.routes.scan import router
from infrastructure.ai.claude_analyzer import ClaudeAnalyzer
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.cache.sqlite_cache import SqliteCache
from infrastructure.external_apis.crtsh_collector import CrtshCollector
from infrastructure.external_apis.dns_collector import DnsCollector
from infrastructure.external_apis.hackertarget_collector import HackerTargetCollector
from infrastructure.external_apis.jarm_collector import JarmCollector
from infrastructure.external_apis.networkx_graph import NetworkXGraphBuilder
from infrastructure.external_apis.urlscan_collector import UrlscanCollector
from infrastructure.external_apis.whois_collector import WhoisCollector


def create_app() -> FastAPI:
    app = FastAPI(title="Domain-Fingerprinting-Tool")

    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    cache = RedisCache() if os.getenv("APP_ENV") == "production" else SqliteCache()

    collectors = [
        WhoisCollector(),
        DnsCollector(),
        UrlscanCollector(),
        CrtshCollector(),
        JarmCollector(),
    ]

    use_case = ScanDomainUseCase(
        cache=cache,
        collector_svc=CollectorService(
            collectors=collectors,
            hackertarget=HackerTargetCollector(),
        ),
        analyzer_svc=AnalyzerService(),
        graph_builder=NetworkXGraphBuilder(),
        data_prepper=DataPrepper(),
        ai_analyzer=ClaudeAnalyzer(),
    )

    app.state.scan_use_case = use_case
    app.include_router(router)

    return app


app = create_app()
