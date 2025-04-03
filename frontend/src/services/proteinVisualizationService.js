// frontend/src/services/proteinVisualizationService.js
import * as d3 from 'd3'
import { getAminoAcidClass, getNodeColor, translateType } from '../utils/proteinUtils'

export function drawProteinGraph(container, sequence, width, height, callbacks) {
  if (!sequence || sequence.length === 0) return { svg: null, g: null }

  // 清除之前的图形
  d3.select(container).selectAll('*').remove()

  // 创建SVG并设置尺寸
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])
    .attr('style', 'max-width: 100%; height: auto;')

  // 创建一个容器组来放置所有图形元素
  const g = svg.append('g')

  // 添加缩放行为
  const zoomBehavior = d3.zoom()
    .scaleExtent([0.1, 5])
    .on('zoom', (event) => {
      if (callbacks.onZoom) callbacks.onZoom(event.transform.k)
      g.attr('transform', event.transform)
    })

  svg.call(zoomBehavior)

  // 创建节点数据
  const nodes = Array.from(sequence).map((aa, i) => ({
    id: i,
    aa: aa,
    group: getAminoAcidClass(aa),
    x: width / 2 + (Math.cos(i * 2 * Math.PI / sequence.length) * width / 3 * Math.min(1, 30 / sequence.length)),
    y: height / 2 + (Math.sin(i * 2 * Math.PI / sequence.length) * height / 3 * Math.min(1, 30 / sequence.length))
  }))

  // 创建连线数据（相邻氨基酸之间的连接）
  const links = Array.from({ length: sequence.length - 1 }, (_, i) => ({
    source: i,
    target: i + 1,
    value: 1
  }))

  // 创建力导向图布局
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(15))
    .force('charge', d3.forceManyBody().strength(-30))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(10))

  // 绘制连线
  const link = g.append('g')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke-width', d => Math.sqrt(d.value))

  // 创建节点组
  const nodeGroups = g.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .attr('class', 'node-group')
    .call(drag(simulation))

  // 为节点组添加提示信息
  nodeGroups.append('title')
    .text(d => `${d.aa} (位置: ${d.id + 1}, 类型: ${translateType(d.group)})`)

  // 绘制节点圆圈
  nodeGroups.append('circle')
    .attr('r', 8)
    .attr('fill', d => getNodeColor(d.group))
    .attr('stroke', '#fff')
    .attr('stroke-width', 1.5)

  // 添加氨基酸标签
  nodeGroups.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '.3em')
    .attr('fill', '#fff')
    .attr('font-weight', 'bold')
    .attr('font-size', '8px')
    .text(d => d.aa)

  // 仅对部分节点（每5个）显示位置编号
  nodeGroups.filter(d => d.id % 5 === 0)
    .append('text')
    .attr('y', -12)
    .attr('text-anchor', 'middle')
    .attr('fill', '#666')
    .attr('font-size', '8px')
    .text(d => d.id + 1)

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    nodeGroups.attr('transform', d => `translate(${d.x},${d.y})`)
  })

  return { svg, g, zoomBehavior }
}

function drag(simulation) {
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    event.subject.fx = event.subject.x
    event.subject.fy = event.subject.y
  }

  function dragged(event) {
    event.subject.fx = event.x
    event.subject.fy = event.y
  }

  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0)
    event.subject.fx = null
    event.subject.fy = null
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended)
}

export function zoomSvg(svgElement, zoomBehavior, scaleFactor) {
  if (!svgElement || !zoomBehavior) return
  d3.select(svgElement)
    .transition()
    .duration(300)
    .call(zoomBehavior.scaleBy, scaleFactor)
}

export function resetZoomSvg(svgElement, zoomBehavior) {
  if (!svgElement || !zoomBehavior) return
  d3.select(svgElement)
    .transition()
    .duration(500)
    .call(zoomBehavior.transform, d3.zoomIdentity)
}