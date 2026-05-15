import asyncio
import os

import httpx

from core.ports.collector_port import ICollector


class UrlscanCollector(ICollector):
    BASE = "https://urlscan.io/api/v1"

    async def fetch(self, domain: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{self.BASE}/scan/",
                    headers={"API-Key": os.getenv("URLSCAN_API_KEY")},
                    json={"url": f"https://{domain}", "visibility": "public"},
                )
                uuid = r.json()["uuid"]

                await asyncio.sleep(15)

                result = await client.get(f"{self.BASE}/result/{uuid}/")
                data = result.json()

            return {
                "urlscan_ip":            data.get("page", {}).get("ip"),
                "urlscan_analytics_ids": self._extract_analytics(data),
                "urlscan_outbound":      self._extract_outbound(data),
                "urlscan_technologies":  data.get("verdicts", {}).get("overall", {}).get("tags", []),
            }
        except Exception as e:
            return {"urlscan_error": str(e)}

    def _extract_analytics(self, data: dict) -> list[str]:
        ids = []
        for g in data.get("data", {}).get("globals", []):
            val = str(g.get("val", ""))
            if any(val.startswith(p) for p in ("G-", "UA-", "GTM-")):
                ids.append(val)
        return list(set(ids))

    def _extract_outbound(self, data: dict) -> list[str]:
        links = data.get("data", {}).get("links", [])
        return [link.get("href", "") for link in links if link.get("href")]
