from dns import asyncresolver
from dns.exception import DNSException

from core.ports.collector_port import ICollector


class DnsCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        result = {}
        for rtype in ["A", "MX", "NS", "TXT"]:
            try:
                answers = await asyncresolver.resolve(domain, rtype)
                result[f"dns_{rtype.lower()}"] = [str(r) for r in answers]
            except DNSException:
                result[f"dns_{rtype.lower()}"] = []
        return result
