import pytest

from infrastructure.external_apis.networkx_graph import NetworkXGraphBuilder

builder = NetworkXGraphBuilder()


def _edge_exists(graph, source, target, relation):
    return any(
        e.source == source and e.target == target and e.relation == relation
        for e in graph.edges
    )


def _node_exists(graph, node_id):
    return any(n.id == node_id for n in graph.nodes)


def test_resolves_to_edge_from_dns_a():
    graph = builder.build({"domain": "example.com", "dns_a": ["1.2.3.4"]})
    assert _edge_exists(graph, "example.com", "1.2.3.4", "resolves_to")


def test_resolves_to_edge_for_each_ip():
    graph = builder.build({"domain": "example.com", "dns_a": ["1.2.3.4", "5.6.7.8"]})
    assert _edge_exists(graph, "example.com", "1.2.3.4", "resolves_to")
    assert _edge_exists(graph, "example.com", "5.6.7.8", "resolves_to")


def test_ip_neighbor_edges_from_ht_neighbors():
    graph = builder.build({
        "domain":       "example.com",
        "dns_a":        ["1.2.3.4"],
        "ht_ip":        "1.2.3.4",
        "ht_neighbors": ["evil.com", "phish.net"],
    })
    assert _edge_exists(graph, "1.2.3.4", "evil.com",  "ip_neighbor")
    assert _edge_exists(graph, "1.2.3.4", "phish.net", "ip_neighbor")


def test_ip_neighbor_falls_back_to_dns_a_when_no_ht_ip():
    graph = builder.build({
        "domain":       "example.com",
        "dns_a":        ["1.2.3.4"],
        "ht_neighbors": ["evil.com"],
    })
    assert _edge_exists(graph, "1.2.3.4", "evil.com", "ip_neighbor")


def test_analytics_id_edge():
    graph = builder.build({
        "domain":                "example.com",
        "urlscan_analytics_ids": ["G-ABC123", "GTM-XYZ"],
    })
    assert _edge_exists(graph, "example.com", "G-ABC123", "analytics_id")
    assert _edge_exists(graph, "example.com", "GTM-XYZ",  "analytics_id")


def test_jarm_hash_and_c2_match_edges():
    graph = builder.build({
        "domain":        "example.com",
        "jarm_hash":     "2ad2ad0002ad2ad00042d42d0000002ad2ad",
        "jarm_c2_match": "Cobalt Strike default",
    })
    assert _edge_exists(graph, "example.com", "2ad2ad0002ad2ad00042d42d0000002ad2ad", "jarm_hash")
    assert _edge_exists(graph, "2ad2ad0002ad2ad00042d42d0000002ad2ad", "Cobalt Strike default", "c2_match")


def test_tls_subdomain_edges_first_10_only():
    subdomains = [f"sub{i}.example.com" for i in range(15)]
    graph = builder.build({"domain": "example.com", "crtsh_subdomains": subdomains})
    tls_edges = [e for e in graph.edges if e.relation == "tls_subdomain"]
    assert len(tls_edges) == 10


def test_empty_raw_data_returns_empty_graph():
    graph = builder.build({})
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0


def test_no_duplicate_nodes():
    # domain appears in dns_a context AND as main node
    graph = builder.build({
        "domain": "example.com",
        "dns_a":  ["1.2.3.4"],
        "ht_ip":  "1.2.3.4",
        "ht_neighbors": ["other.com"],
    })
    ip_nodes = [n for n in graph.nodes if n.id == "1.2.3.4"]
    assert len(ip_nodes) == 1
