from core.domain.entities.threat_graph import ThreatGraph


class DataPrepper:
    def prepare(self, graph: ThreatGraph, analysis: dict) -> str:
        lines = [
            f"{e.source} → {e.target} [{e.relation}]"
            for e in graph.edges
        ]

        risk = analysis.get("risk_score", 0)
        risk_value = risk.value if hasattr(risk, "value") else risk
        lines.append(f"overall_risk_score: {risk_value}/100")

        if analysis.get("jarm_c2_match"):
            lines.append(f"jarm_c2_match: {analysis['jarm_c2_match']}")

        if analysis.get("domain_age_days") is not None:
            lines.append(f"domain_age: {self._format_age(analysis['domain_age_days'])}")

        return "\n".join(lines)

    @staticmethod
    def _format_age(days: int) -> str:
        if days < 30:
            return f"{days} days"
        if days < 365:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''}"
        years  = days // 365
        months = (days % 365) // 30
        if months == 0:
            return f"{years} year{'s' if years > 1 else ''}"
        return f"{years} year{'s' if years > 1 else ''}, {months} month{'s' if months > 1 else ''}"
