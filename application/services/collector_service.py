import asyncio

from core.ports.collector_port import ICollector
from infrastructure.external_apis.hackertarget_collector import HackerTargetCollector


class CollectorService:
    def __init__(self, collectors: list[ICollector], hackertarget: HackerTargetCollector):
        self._collectors   = collectors
        self._hackertarget = hackertarget

    async def collect_all(self, domain: str) -> dict:
        results = await asyncio.gather(
            *[c.fetch(domain) for c in self._collectors],
            return_exceptions=True,
        )
        merged: dict = {}
        for r in results:
            if isinstance(r, Exception):
                continue
            merged.update(r)

        ip = (merged.get("dns_a") or [None])[0]
        if ip:
            ht_result = await self._hackertarget.fetch(domain, ip=ip)
            merged.update(ht_result)

        return merged
