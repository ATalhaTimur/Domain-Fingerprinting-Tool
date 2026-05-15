from dataclasses import dataclass, field


@dataclass
class ThreatNode:
    id: str
    type: str  # domain | ip | analytics_id | jarm_hash
    metadata: dict = field(default_factory=dict)


@dataclass
class ThreatEdge:
    source: str
    target: str
    relation: str  # resolves_to | ip_neighbor | analytics_shared | c2_match


@dataclass
class ThreatGraph:
    nodes: list[ThreatNode] = field(default_factory=list)
    edges: list[ThreatEdge] = field(default_factory=list)

    def add_node(self, node: ThreatNode) -> None:
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)

    def add_edge(self, edge: ThreatEdge) -> None:
        self.edges.append(edge)
