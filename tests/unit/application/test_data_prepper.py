from core.domain.entities.risk_score import RiskScore
from core.domain.entities.threat_graph import ThreatEdge, ThreatGraph, ThreatNode
from application.services.data_prepper import DataPrepper

prepper = DataPrepper()


def _graph(*edges: tuple[str, str, str]) -> ThreatGraph:
    g = ThreatGraph()
    for source, target, relation in edges:
        g.add_node(ThreatNode(id=source, type="domain"))
        g.add_node(ThreatNode(id=target, type="ip"))
        g.add_edge(ThreatEdge(source=source, target=target, relation=relation))
    return g


def test_output_contains_all_edges():
    graph = _graph(
        ("example.com", "1.2.3.4",    "resolves_to"),
        ("1.2.3.4",     "evil.com",   "ip_neighbor"),
        ("example.com", "UA-99999999","analytics_id"),
    )
    out = prepper.prepare(graph, {"risk_score": RiskScore(30)})
    assert "example.com → 1.2.3.4 [resolves_to]" in out
    assert "1.2.3.4 → evil.com [ip_neighbor]" in out
    assert "example.com → UA-99999999 [analytics_id]" in out


def test_output_does_not_contain_coordinates_or_colors():
    graph = _graph(("example.com", "1.2.3.4", "resolves_to"))
    # add visual metadata that should never leak into the text
    graph.nodes[0].metadata.update({"x": 342.18, "y": -119.44, "color": "#e74c3c", "radius": 12})
    graph.edges[0].metadata = {"strokeWidth": 2} if hasattr(graph.edges[0], "metadata") else None
    out = prepper.prepare(graph, {"risk_score": RiskScore(0)})
    for noise in ("342.18", "-119.44", "#e74c3c", "radius", "strokeWidth", "color"):
        assert noise not in out, f"visual noise '{noise}' must not appear in output"


def test_risk_score_line_always_present():
    graph = ThreatGraph()
    out = prepper.prepare(graph, {"risk_score": RiskScore(0)})
    assert "overall_risk_score:" in out


def test_risk_score_value_in_output():
    graph = ThreatGraph()
    out = prepper.prepare(graph, {"risk_score": RiskScore(75)})
    assert "overall_risk_score: 75/100" in out


def test_jarm_c2_match_included_when_present():
    graph = ThreatGraph()
    out = prepper.prepare(graph, {
        "risk_score":   RiskScore(40),
        "jarm_c2_match": "Cobalt Strike default",
    })
    assert "jarm_c2_match: Cobalt Strike default" in out


def test_jarm_c2_match_absent_when_none():
    graph = ThreatGraph()
    out = prepper.prepare(graph, {"risk_score": RiskScore(0), "jarm_c2_match": None})
    assert "jarm_c2_match" not in out


def test_domain_age_included_when_present():
    graph = ThreatGraph()
    out = prepper.prepare(graph, {"risk_score": RiskScore(0), "domain_age_days": 3})
    assert "domain_age_days: 3" in out


def test_domain_age_absent_when_none():
    graph = ThreatGraph()
    out = prepper.prepare(graph, {"risk_score": RiskScore(0), "domain_age_days": None})
    assert "domain_age_days" not in out
