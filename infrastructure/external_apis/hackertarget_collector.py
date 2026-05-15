import httpx

from core.ports.collector_port import ICollector


class HackerTargetCollector(ICollector):
    async def fetch(self, domain: str, ip: str = "") -> dict:
        if not ip:
            return {"ht_neighbors": [], "ht_note": "no ip provided"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
                )
            if "error" in r.text.lower():
                return {"ht_neighbors": [], "ht_error": r.text}
            neighbors = [line.strip() for line in r.text.splitlines() if line.strip()]
            return {"ht_ip": ip, "ht_neighbors": neighbors}
        except Exception as e:
            return {"ht_error": str(e), "ht_neighbors": []}
