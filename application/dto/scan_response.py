from dataclasses import dataclass
from datetime import datetime

from core.domain.entities.domain_target import DomainTarget
from core.domain.entities.risk_score import RiskScore
from core.domain.entities.scan import Scan, ScanStatus
from core.domain.entities.threat_graph import ThreatEdge, ThreatGraph, ThreatNode


@dataclass
class ScanResponseDTO:
    scan:    Scan
    graph:   ThreatGraph
    summary: str

    def to_dict(self) -> dict:
        return {
            "scan": {
                "id":           self.scan.id,
                "target":       self.scan.target.value,
                "status":       self.scan.status.value,
                "risk_score":   self.scan.risk_score.value,
                "raw_data":     self.scan.raw_data,
                "created_at":   self.scan.created_at.isoformat(),
                "completed_at": self.scan.completed_at.isoformat() if self.scan.completed_at else None,
            },
            "graph": {
                "nodes": [
                    {"id": n.id, "type": n.type, "metadata": n.metadata}
                    for n in self.graph.nodes
                ],
                "edges": [
                    {"source": e.source, "target": e.target, "relation": e.relation}
                    for e in self.graph.edges
                ],
            },
            "summary": self.summary,
        }

    @classmethod
    def from_cache(cls, data: dict) -> "ScanResponseDTO":
        s = data["scan"]
        scan = Scan(
            id=s["id"],
            target=DomainTarget(s["target"]),
            status=ScanStatus(s["status"]),
            risk_score=RiskScore(s["risk_score"]),
            raw_data=s["raw_data"],
            created_at=datetime.fromisoformat(s["created_at"]),
            completed_at=datetime.fromisoformat(s["completed_at"]) if s["completed_at"] else None,
        )
        g = data["graph"]
        graph = ThreatGraph(
            nodes=[ThreatNode(id=n["id"], type=n["type"], metadata=n.get("metadata", {})) for n in g["nodes"]],
            edges=[ThreatEdge(source=e["source"], target=e["target"], relation=e["relation"]) for e in g["edges"]],
        )
        return cls(scan=scan, graph=graph, summary=data["summary"])
