import asyncio
import json
import os
from enum import Enum

from dotenv import load_dotenv
import typer

load_dotenv()

from application.dto.scan_request import ScanRequestDTO
from application.services.analyzer_service import AnalyzerService
from application.services.collector_service import CollectorService
from application.services.data_prepper import DataPrepper
from application.use_cases.scan_domain import ScanDomainUseCase
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

app = typer.Typer(name="dft", help="Domain Fingerprinting Tool")


class Mode(str, Enum):
    technical = "technical"
    executive = "executive"


class Output(str, Enum):
    text = "text"
    json = "json"


def _build_use_case() -> ScanDomainUseCase:
    cache = RedisCache() if os.getenv("APP_ENV") == "production" else SqliteCache()
    return ScanDomainUseCase(
        cache=cache,
        collector_svc=CollectorService(
            collectors=[
                WhoisCollector(),
                DnsCollector(),
                UrlscanCollector(),
                CrtshCollector(),
                JarmCollector(),
            ],
            hackertarget=HackerTargetCollector(),
        ),
        analyzer_svc=AnalyzerService(),
        graph_builder=NetworkXGraphBuilder(),
        data_prepper=DataPrepper(),
        ai_analyzer=ClaudeAnalyzer(),
    )


@app.command()
def scan(
    domain: str = typer.Argument(..., help="Domain or URL to scan"),
    mode: Mode = typer.Option(Mode.technical, "--mode", "-m", help="Analysis mode"),
    output: Output = typer.Option(Output.text, "--output", "-o", help="Output format"),
) -> None:
    """Scan a domain and print a threat intelligence summary."""
    use_case = _build_use_case()
    request  = ScanRequestDTO(target=domain, mode=mode.value)

    try:
        result = asyncio.run(use_case.execute(request))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if output == Output.json:
        typer.echo(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        typer.echo(result.summary)


if __name__ == "__main__":
    app()
