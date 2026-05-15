import pytest
from core.domain.entities.threat_graph import ThreatEdge, ThreatGraph, ThreatNode


def test_add_node_deduplication():
    graph = ThreatGraph()
    node = ThreatNode(id="n1", type="domain")
    graph.add_node(node)
    graph.add_node(node)
    assert len(graph.nodes) == 1


def test_add_node_deduplication_same_id_different_object():
    graph = ThreatGraph()
    graph.add_node(ThreatNode(id="n1", type="domain"))
    graph.add_node(ThreatNode(id="n1", type="ip"))  # same id, different type
    assert len(graph.nodes) == 1


def test_add_node_distinct_ids():
    graph = ThreatGraph()
    graph.add_node(ThreatNode(id="n1", type="domain"))
    graph.add_node(ThreatNode(id="n2", type="ip"))
    assert len(graph.nodes) == 2


def test_add_edge_always_appends():
    graph = ThreatGraph()
    edge = ThreatEdge(source="n1", target="n2", relation="resolves_to")
    graph.add_edge(edge)
    graph.add_edge(edge)
    assert len(graph.edges) == 2


def test_add_edge_appends_distinct_edges():
    graph = ThreatGraph()
    graph.add_edge(ThreatEdge(source="n1", target="n2", relation="resolves_to"))
    graph.add_edge(ThreatEdge(source="n2", target="n3", relation="ip_neighbor"))
    assert len(graph.edges) == 2


@pytest.mark.parametrize("node_type", ["domain", "ip", "analytics_id", "jarm_hash"])
def test_node_types(node_type):
    node = ThreatNode(id="n1", type=node_type)
    graph = ThreatGraph()
    graph.add_node(node)
    assert graph.nodes[0].type == node_type


@pytest.mark.parametrize("relation", ["resolves_to", "ip_neighbor", "analytics_shared", "c2_match"])
def test_edge_relations(relation):
    edge = ThreatEdge(source="a", target="b", relation=relation)
    graph = ThreatGraph()
    graph.add_edge(edge)
    assert graph.edges[0].relation == relation
