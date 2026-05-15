import * as d3 from 'd3'

const NODE_COLORS = {
  domain:       '#4a9eff',
  ip:           '#5dade2',
  analytics_id: '#a569bd',
  jarm_hash:    '#f39c12',
  c2_name:      '#e74c3c',
}

const EDGE_COLORS = {
  resolves_to:   '#4a9eff55',
  ip_neighbor:   '#5dade255',
  analytics_id:  '#a569bd55',
  jarm_hash:     '#f39c1255',
  c2_match:      '#e74c3c88',
  tls_subdomain: '#5dade255',
}

const RISK_COLORS = { critical: '#e74c3c', medium: '#f39c12', low: '#2ecc71' }

function riskLevel(score) {
  if (score >= 70) return 'critical'
  if (score >= 40) return 'medium'
  return 'low'
}

export function renderGraph(container, data, onNodeClick) {
  d3.select(container).selectAll('svg').remove()

  const width  = container.clientWidth  || 800
  const height = container.clientHeight || 500
  const tooltip = document.getElementById('dft-tooltip')

  const zoom = d3.zoom()
    .scaleExtent([0.15, 5])
    .on('zoom', (event) => g.attr('transform', event.transform))

  const svg = d3.select(container)
    .append('svg')
    .attr('width',  '100%')
    .attr('height', '100%')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .call(zoom)

  svg.on('click', () => {
    node.attr('opacity', 1)
    link.attr('opacity', 0.7)
    linkLabel.attr('opacity', 1)
    if (tooltip) tooltip.style.display = 'none'
  })

  const defs = svg.append('defs')

  ;[['arrow-default', '#444'], ['arrow-c2', '#e74c3c'], ['arrow-accent', '#4a9eff']].forEach(([id, color]) => {
    defs.append('marker').attr('id', id)
      .attr('viewBox', '0 -5 10 10').attr('refX', 22).attr('refY', 0)
      .attr('markerWidth', 5).attr('markerHeight', 5).attr('orient', 'auto')
      .append('path').attr('d', 'M0,-5L10,0L0,5').attr('fill', color)
  })

  const filter = defs.append('filter').attr('id', 'glow')
  filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur')
  const feMerge = filter.append('feMerge')
  feMerge.append('feMergeNode').attr('in', 'coloredBlur')
  feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

  const g = svg.append('g')

  const target    = data.scan.target
  const riskScore = data.scan.risk_score
  const nodes     = data.graph.nodes.map(n => ({ ...n }))
  const links     = data.graph.edges.map(e => ({ ...e }))

  const linkedByIndex = {}
  links.forEach(l => {
    linkedByIndex[`${l.source},${l.target}`] = true
    linkedByIndex[`${l.target},${l.source}`] = true
  })
  const isConnected = (a, b) => a.id === b.id || linkedByIndex[`${a.id},${b.id}`]

  const nodeCount      = nodes.length
  const chargeStrength = nodeCount > 30 ? -600 : -400
  const linkDistance   = nodeCount > 30 ? 100 : 130

  const simulation = d3.forceSimulation(nodes)
    .force('link',    d3.forceLink(links).id(d => d.id).distance(linkDistance))
    .force('charge',  d3.forceManyBody().strength(chargeStrength))
    .force('center',  d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide(d => d.id === target ? 20 : 14))

  const link = g.append('g')
    .selectAll('line').data(links).join('line')
    .attr('stroke', d => EDGE_COLORS[d.relation] || '#44444488')
    .attr('stroke-width', d => d.relation === 'c2_match' ? 2.5 : 1.5)
    .attr('marker-end', d => {
      if (d.relation === 'c2_match')  return 'url(#arrow-c2)'
      if (d.relation === 'resolves_to') return 'url(#arrow-accent)'
      return 'url(#arrow-default)'
    })
    .attr('opacity', 0.7)

  const linkLabel = g.append('g')
    .selectAll('text').data(links).join('text')
    .attr('fill', '#555').attr('font-size', '8px')
    .attr('text-anchor', 'middle').attr('pointer-events', 'none')
    .text(d => d.relation.replace(/_/g, ' '))

  const node = g.append('g')
    .selectAll('circle').data(nodes).join('circle')
    .attr('r', d => d.id === target ? 15 : d.type === 'c2_name' ? 12 : 9)
    .attr('fill', d => d.id === target ? RISK_COLORS[riskLevel(riskScore)] : NODE_COLORS[d.type] || '#888')
    .attr('stroke', d => d.id === target ? '#fff' : d.type === 'c2_name' ? '#e74c3c' : '#1c2128')
    .attr('stroke-width', d => d.id === target ? 2.5 : d.type === 'c2_name' ? 2 : 1.2)
    .attr('filter', d => d.type === 'c2_name' ? 'url(#glow)' : null)
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y })
      .on('end',   (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null })
    )
    .on('mouseover', (event, d) => {
      node.attr('opacity', n => isConnected(d, n) ? 1 : 0.25)
      link.attr('opacity', l => (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.08)
      linkLabel.attr('opacity', l => (l.source.id === d.id || l.target.id === d.id) ? 1 : 0)
      if (tooltip) {
        tooltip.querySelector('#tt-id').textContent   = d.id
        tooltip.querySelector('#tt-type').textContent = d.type.replace(/_/g, ' ')
        tooltip.style.display = 'block'
      }
    })
    .on('mousemove', (event) => {
      if (tooltip) {
        tooltip.style.left = (event.clientX + 14) + 'px'
        tooltip.style.top  = (event.clientY - 10) + 'px'
      }
    })
    .on('mouseout', () => {
      node.attr('opacity', 1)
      link.attr('opacity', 0.7)
      linkLabel.attr('opacity', 1)
      if (tooltip) tooltip.style.display = 'none'
    })
    .on('click', (event, d) => {
      event.stopPropagation()
      onNodeClick(d)
      node.attr('stroke', n => n.id === d.id || n.id === target ? '#fff' : n.type === 'c2_name' ? '#e74c3c' : '#1c2128')
          .attr('stroke-width', n => n.id === d.id ? 3 : n.id === target ? 2.5 : n.type === 'c2_name' ? 2 : 1.2)
    })

  const label = g.append('g')
    .selectAll('text').data(nodes).join('text')
    .attr('fill', d => d.id === target ? '#f0f6fc' : '#9da8b2')
    .attr('font-size', d => d.id === target ? '11px' : '9.5px')
    .attr('font-weight', d => d.id === target ? '600' : '400')
    .attr('text-anchor', 'middle')
    .attr('dy', d => (d.id === target ? 15 : 9) + 7 + 'px')
    .attr('pointer-events', 'none')
    .text(d => { const max = d.id === target ? 24 : 18; return d.id.length > max ? d.id.slice(0, max - 1) + '…' : d.id })

  simulation.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    linkLabel.attr('x', d => (d.source.x + d.target.x) / 2)
             .attr('y', d => (d.source.y + d.target.y) / 2 - 3)
    node.attr('cx', d => d.x).attr('cy', d => d.y)
    label.attr('x', d => d.x).attr('y', d => d.y)
  })

  return { svg: svg.node(), zoom }
}
