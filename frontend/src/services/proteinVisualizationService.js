// frontend/src/services/proteinVisualizationService.js
import * as d3 from 'd3'
import { getAminoAcidClass, getNodeColor, translateType } from '../utils/proteinUtils'

export function drawProteinGraph(container, sequence, width, height, callbacks, {
  secondaryStructure = [],
  functionalSites = []
} = {}) {
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
      if (callbacks?.onZoom) callbacks.onZoom(event.transform.k)
      g.attr('transform', event.transform)
    })

  svg.call(zoomBehavior)

  // 使用螺旋初始布局优化节点分布
  const nodes = Array.from(sequence).map((aa, i) => {
    // 螺旋系数调整，根据序列长度动态调整半径
    const spiralRadius = Math.min(width, height) * 0.35 * (1 - i / (2 * sequence.length));
    const angle = i * (sequence.length > 100 ? 0.3 : 0.5); // 控制螺旋紧密度
    return {
      id: i,
      aa: aa,
      group: getAminoAcidClass(aa),
      structure: secondaryStructure[i] || 'C',
      x: width / 2 + spiralRadius * Math.cos(angle),
      y: height / 2 + spiralRadius * Math.sin(angle)
    };
  });

  // 创建连线数据（相邻氨基酸之间的连接）
  const links = Array.from({ length: sequence.length - 1 }, (_, i) => ({
    source: i,
    target: i + 1,
    value: 1,
    isPeptideBond: i % 10 === 9 // 每10个氨基酸标记一个肽键
  }))

  // 优化力导向图参数，根据序列长度动态调整
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id)
      .distance(d => Math.min(30, 40 - sequence.length / 50))) // 动态链接长度
    .force('charge', d3.forceManyBody()
      .strength(d => Math.min(-30, -80 / Math.sqrt(Math.max(50, sequence.length)))))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(10))
    .force('x', d3.forceX(width / 2).strength(0.01))
    .force('y', d3.forceY(height / 2).strength(0.01))

  // 添加降温安排，避免布局永远不稳定
  simulation.alphaDecay(sequence.length > 100 ? 0.03 : 0.028)

  // 添加图例
  addLegend(svg, width)

  // 绘制连线 - 区分普通连接和肽键
  const link = g.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', d => d.isPeptideBond ? 2 : 1)
    .attr('stroke-dasharray', d => d.isPeptideBond ? '3,2' : null)

  // 创建节点组
  const nodeGroups = g.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .attr('class', d => {
      const classes = ['node-group'];
      // 添加二级结构类名
      if (d.structure) {
        classes.push(`structure-${d.structure}`);
      }
      // 添加功能位点类名
      const site = functionalSites.find(site =>
        d.id >= site.position && d.id < site.position + site.length
      );
      if (site) {
        classes.push(site.type);
      }
      return classes.join(' ');
    })
    .call(drag(simulation))

  // 为节点组添加提示信息（增强显示结构和功能信息）
  nodeGroups.append('title')
    .text(d => {
      let title = `${d.aa} (位置: ${d.id + 1}, 类型: ${translateType(d.group)})`;

      // 添加结构信息
      if (d.structure === 'H') title += ', 结构: α-螺旋';
      else if (d.structure === 'E') title += ', 结构: β-折叠';
      else title += ', 结构: 无规卷曲';

      // 添加功能位点信息
      const site = functionalSites.find(site =>
        d.id >= site.position && d.id < site.position + site.length
      );
      if (site) {
        title += `, ${site.description}`;
      }

      return title;
    })

  // 根据二级结构和功能位点增强节点显示
  nodeGroups.append('circle')
    .attr('r', d => {
      // 每5个位置的氨基酸稍大
      return d.id % 5 === 0 ? 9 : 8;
    })
    .attr('fill', d => {
      // 基本颜色基于氨基酸类型
      const baseColor = getNodeColor(d.group);

      // 如果有二级结构信息，调整颜色
      if (d.structure === 'H') return d3.color(baseColor).brighter(0.3);
      if (d.structure === 'E') return d3.color(baseColor).darker(0.3);
      return baseColor;
    })
    .attr('stroke', d => {
      // 功能位点特殊边框颜色
      const site = functionalSites.find(site =>
        d.id >= site.position && d.id < site.position + site.length
      );
      if (site) {
        if (site.type === 'active-site') return '#F56C6C';
        if (site.type === 'binding-site') return '#409EFF';
        if (site.type === 'ptm-site') return '#67C23A';
      }
      // 每10个位置特殊标记
      return d.id % 10 === 0 ? '#000' : '#fff';
    })
    .attr('stroke-width', d => {
      // 功能位点加粗边框
      const isFunctionalSite = functionalSites.some(site =>
        d.id >= site.position && d.id < site.position + site.length
      );
      return isFunctionalSite ? 2.5 : (d.id % 10 === 0 ? 2 : 1.5);
    })

  // 添加氨基酸标签
  nodeGroups.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '.3em')
    .attr('fill', d => {
      // 根据二级结构调整标签颜色，保证可读性
      if (d.structure === 'H' || d.structure === 'E') {
        const color = getNodeColor(d.group);
        return d3.lab(color).l < 50 ? '#fff' : '#000';
      }
      return '#fff';
    })
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

  // 性能优化：针对不同大小的序列优化刷新策略
  if (sequence.length > 200) {
    // 大型序列性能优化：减少更新频率
    let tickCounter = 0;
    simulation.on('tick', () => {
      tickCounter++;
      if (tickCounter % 3 !== 0) return; // 每三帧更新一次

      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      nodeGroups.attr('transform', d => `translate(${d.x},${d.y})`)
    });

    // 设置较短的模拟时间
    simulation.alpha(1).alphaDecay(0.03).restart();
  } else {
    // 对于小序列，保持原有行为
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      nodeGroups.attr('transform', d => `translate(${d.x},${d.y})`)
    });
  }

  return { svg, g, zoomBehavior }
}

// 添加图例函数
function addLegend(svg, width) {
  const legend = svg.append('g')
    .attr('class', 'graph-legend')
    .attr('transform', `translate(${width - 120}, 20)`);

  // 结构图例
  const structures = [
    { type: 'H', color: '#ff7675', label: 'α-螺旋' },
    { type: 'E', color: '#74b9ff', label: 'β-折叠' },
    { type: 'C', color: '#b2bec3', label: '无规卷曲' }
  ];

  // 功能位点图例
  const sites = [
    { type: 'active-site', color: '#F56C6C', label: '活性位点' },
    { type: 'binding-site', color: '#409EFF', label: '结合位点' },
    { type: 'ptm-site', color: '#67C23A', label: '修饰位点' }
  ];

  // 绘制结构图例
  structures.forEach((item, i) => {
    const g = legend.append('g')
      .attr('transform', `translate(0, ${i * 20})`);

    g.append('rect')
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', item.color)
      .attr('rx', 2);

    g.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .attr('font-size', '12px')
      .text(item.label);
  });

  // 绘制功能位点图例
  sites.forEach((item, i) => {
    const g = legend.append('g')
      .attr('transform', `translate(0, ${(i + 4) * 20})`);

    g.append('circle')
      .attr('r', 7)
      .attr('cx', 7)
      .attr('cy', 7)
      .attr('fill', '#ddd')
      .attr('stroke', item.color)
      .attr('stroke-width', 2);

    g.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .attr('font-size', '12px')
      .text(item.label);
  });

  return legend;
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