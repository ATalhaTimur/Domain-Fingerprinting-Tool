import asyncpg

from core.ports.collector_port import ICollector


class CrtshCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        try:
            conn = await asyncpg.connect(
                host="crt.sh", port=5432,
                database="certwatch", user="guest",
                timeout=10,
            )
            rows = await conn.fetch(
                """
                SELECT DISTINCT LOWER(NAME_VALUE) AS name
                FROM certificate_and_identities
                WHERE LOWER(NAME_VALUE) LIKE $1
                ORDER BY name LIMIT 200
                """,
                f"%.{domain.lower()}",
                timeout=9,
            )
            await conn.close()

            subdomains = [r["name"] for r in rows if r["name"] != domain]
            return {"crtsh_subdomains": subdomains, "crtsh_count": len(subdomains)}
        except Exception as e:
            return {"crtsh_error": str(e), "crtsh_subdomains": []}
