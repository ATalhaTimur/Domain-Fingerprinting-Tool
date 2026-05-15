from core.domain.entities.threat_graph import ThreatEdge, ThreatGraph, ThreatNode
from core.ports.graph_port import IGraphBuilder


class NetworkXGraphBuilder(IGraphBuilder):
    def build(self, raw_data: dict) -> ThreatGraph:
        graph  = ThreatGraph()
        domain = raw_data.get("domain", "")

        if domain:
            graph.add_node(ThreatNode(id=domain, type="domain"))

        # domain → IP [resolves_to]
        for ip in raw_data.get("dns_a", []):
            graph.add_node(ThreatNode(id=ip, type="ip"))
            if domain:
                graph.add_edge(ThreatEdge(source=domain, target=ip, relation="resolves_to"))

        # IP → neighbor [ip_neighbor]  (source is the queried IP from HackerTarget)
        ht_ip = raw_data.get("ht_ip") or (raw_data.get("dns_a") or [None])[0]
        if ht_ip:
            graph.add_node(ThreatNode(id=ht_ip, type="ip"))
            for neighbor in raw_data.get("ht_neighbors", []):
                graph.add_node(ThreatNode(id=neighbor, type="domain"))
                graph.add_edge(ThreatEdge(source=ht_ip, target=neighbor, relation="ip_neighbor"))

        # domain → analytics_id [analytics_id]
        for aid in raw_data.get("urlscan_analytics_ids", []):
            graph.add_node(ThreatNode(id=aid, type="analytics_id"))
            if domain:
                graph.add_edge(ThreatEdge(source=domain, target=aid, relation="analytics_id"))

        # domain → jarm_hash [jarm_hash]
        jarm_hash = raw_data.get("jarm_hash")
        if jarm_hash and domain:
            graph.add_node(ThreatNode(id=jarm_hash, type="jarm_hash"))
            graph.add_edge(ThreatEdge(source=domain, target=jarm_hash, relation="jarm_hash"))

            # jarm_hash → c2_name [c2_match]
            c2_match = raw_data.get("jarm_c2_match")
            if c2_match:
                graph.add_node(ThreatNode(id=c2_match, type="c2_name"))
                graph.add_edge(ThreatEdge(source=jarm_hash, target=c2_match, relation="c2_match"))

        # domain → subdomain [tls_subdomain]  (first 10 only)
        for subdomain in raw_data.get("crtsh_subdomains", [])[:10]:
            graph.add_node(ThreatNode(id=subdomain, type="domain"))
            if domain:
                graph.add_edge(ThreatEdge(source=domain, target=subdomain, relation="tls_subdomain"))

        return graph
