import asyncio

from jarm.scanner.scanner import Scanner

from core.ports.collector_port import ICollector


class JarmCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        try:
            jarm_hash = await asyncio.to_thread(Scanner.scan, domain, 443)
            return {"jarm_hash": jarm_hash}
        except Exception as e:
            return {"jarm_error": str(e), "jarm_hash": None}
