import asyncwhois

from core.ports.collector_port import ICollector


class WhoisCollector(ICollector):
    async def fetch(self, domain: str) -> dict:
        try:
            _, parsed = await asyncwhois.aio_whois(domain)
            return {
                "whois_registrar":    parsed.get("registrar"),
                "whois_created":      str(parsed.get("created")),
                "whois_expires":      str(parsed.get("expires")),
                "whois_emails":       parsed.get("emails", []),
                "whois_name_servers": parsed.get("name_servers", []),
            }
        except Exception as e:
            return {"whois_error": str(e)}
