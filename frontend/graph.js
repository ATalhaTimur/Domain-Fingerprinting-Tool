// Node color by type; main domain overridden by risk level after render
const NODE_COLORS = {
  domain:       "#4a9eff",
  ip:           "#5dade2",
  analytics_id: "#a569bd",
  jarm_hash:    "#f39c12",
  c2_name:      "#e74c3c",
};

const RISK_COLORS = {
  critical: "#e74c3c",
  medium:   "#f39c12",
  low:      "#2ecc71",
};

function riskLevel(score) {
  if (score >= 70) return "critical";
  if (score >= 40) return "medium";
  return "low";
}

function renderGraph(containerId, data, onNodeClick) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  const width  = container.clientWidth  || 800;
  const height = container.clientHeight || 500;

  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", `0 0 ${width} ${height}`);

  // Arrow marker for directed edges
  svg.append("defs").append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 20)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#555");

  const g = svg.append("g");

  // Zoom + pan
  svg.call(
    d3.zoom()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => g.attr("transform", event.transform))
  );

  const target    = data.scan.target;
  const riskScore = data.scan.risk_score;
  const nodes     = data.graph.nodes.map(n => ({ ...n }));
  const links     = data.graph.edges.map(e => ({ ...e }));

  const simulation = d3.forceSimulation(nodes)
    .force("link",    d3.forceLink(links).id(d => d.id).distance(120))
    .force("charge",  d3.forceManyBody().strength(-400))
    .force("center",  d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide(30));

  const link = g.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", "#444")
    .attr("stroke-width", 1.5)
    .attr("marker-end", "url(#arrow)");

  const linkLabel = g.append("g")
    .selectAll("text")
    .data(links)
    .join("text")
    .attr("fill", "#666")
    .attr("font-size", "9px")
    .attr("text-anchor", "middle")
    .text(d => d.relation);

  const node = g.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", d => d.id === target ? 14 : 10)
    .attr("fill", d => {
      if (d.id === target) return RISK_COLORS[riskLevel(riskScore)];
      return NODE_COLORS[d.type] || "#888";
    })
    .attr("stroke", d => d.id === target ? "#fff" : "#333")
    .attr("stroke-width", d => d.id === target ? 2 : 1)
    .style("cursor", "pointer")
    .call(
      d3.drag()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag",  (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on("end",   (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
    )
    .on("click", (event, d) => {
      event.stopPropagation();
      onNodeClick(d);
      node.attr("stroke", n => n.id === d.id ? "#fff" : (n.id === target ? "#fff" : "#333"))
          .attr("stroke-width", n => n.id === d.id ? 3 : (n.id === target ? 2 : 1));
    });

  const label = g.append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .attr("fill", "#ccc")
    .attr("font-size", "11px")
    .attr("text-anchor", "middle")
    .attr("dy", "2.2em")
    .text(d => d.id.length > 20 ? d.id.slice(0, 18) + "…" : d.id);

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);

    linkLabel
      .attr("x", d => (d.source.x + d.target.x) / 2)
      .attr("y", d => (d.source.y + d.target.y) / 2);

    node.attr("cx", d => d.x).attr("cy", d => d.y);
    label.attr("x", d => d.x).attr("y", d => d.y);
  });

  return simulation;
}
