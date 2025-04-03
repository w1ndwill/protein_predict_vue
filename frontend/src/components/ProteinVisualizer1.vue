<template>
  <div class="protein-viz-container">
    <el-tabs v-model="activeTab" @tab-click="handleTabChange">

      <el-tab-pane label="序列视图" name="sequence">
        <div class="sequence-view">
          <div class="sequence-container">
            <span
              v-for="(aa, i) in sequence"
              :key="i"
              :class="['aa-residue', getAminoAcidClass(aa)]"
              :title="`${aa} (位置: ${i+1})`"
            >
              {{ aa }}
            </span>
          </div>
          <div class="legend">
            <div class="legend-item">
              <div class="color-box hydrophobic"></div>
              <span>疏水性 (AILFMWV)</span>
            </div>
            <div class="legend-item">
              <div class="color-box hydrophilic"></div>
              <span>亲水性 (STNQ)</span>
            </div>
            <div class="legend-item">
              <div class="color-box positive"></div>
              <span>正电荷 (RHK)</span>
            </div>
            <div class="legend-item">
              <div class="color-box negative"></div>
              <span>负电荷 (DE)</span>
            </div>
            <div class="legend-item">
              <div class="color-box special"></div>
              <span>特殊 (CGPY)</span>
            </div>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="图拓扑结构" name="graph">
        <div class="graph-controls">
          <div>
            <el-button-group>
              <el-button @click="zoomIn" :icon="Plus" size="small" title="放大"></el-button>
              <el-button @click="zoomOut" :icon="Minus" size="small" title="缩小"></el-button>
              <el-button @click="resetZoom" :icon="Refresh" size="small" title="重置视图"></el-button>
            </el-button-group>
            <span class="zoom-level">缩放: {{Math.round(currentZoom * 100)}}%</span>
          </div>
          <div class="graph-note">提示: 可拖拽节点调整位置</div>
        </div>
        <div ref="graphContainer" class="graph-container"></div>
        <div class="graph-legend">
          <div class="graph-note">图例说明: 每个圆圈表示氨基酸残基，连线表示肽链连接</div>
          <div class="legend">
            <div class="legend-item">
              <div class="color-box hydrophobic"></div>
              <span>疏水性 (AILFMWV)</span>
            </div>
            <div class="legend-item">
              <div class="color-box hydrophilic"></div>
              <span>亲水性 (STNQ)</span>
            </div>
            <div class="legend-item">
              <div class="color-box positive"></div>
              <span>正电荷 (RHK)</span>
            </div>
            <div class="legend-item">
              <div class="color-box negative"></div>
              <span>负电荷 (DE)</span>
            </div>
            <div class="legend-item">
              <div class="color-box special"></div>
              <span>特殊 (CGPY)</span>
            </div>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="二级结构预测" name="structure">
        <div class="structure-view">
          <div class="prediction-info">
            <el-alert type="info" :closable="false">
              <template #title>
                <span>基于简化规则的二级结构预测（仅供参考）</span>
              </template>
              <div slot="description">
                本预测基于氨基酸倾向性统计，非专业算法结果
              </div>
            </el-alert>
          </div>
          <div class="structure-container">
            <div class="sequence-line">
              <span
                v-for="(aa, i) in sequence"
                :key="`aa-${i}`"
                class="structure-aa"
              >
                {{ aa }}
              </span>
            </div>
            <div class="structure-line">
              <span
                v-for="(struct, i) in predictedStructure"
                :key="`struct-${i}`"
                :class="['structure-symbol', getStructureClass(struct)]"
                :title="getStructureTitle(struct)"
              >
                {{ struct }}
              </span>
            </div>
          </div>
          <div class="structure-legend">
            <div class="legend-item">
              <div class="structure-box helix"></div>
              <span>α螺旋 (H)</span>
            </div>
            <div class="legend-item">
              <div class="structure-box sheet"></div>
              <span>β折叠 (E)</span>
            </div>
            <div class="legend-item">
              <div class="structure-box coil"></div>
              <span>无规卷曲 (C)</span>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import * as d3 from 'd3'
import { Plus, Minus, Refresh } from '@element-plus/icons-vue'

export default {
  components: {
    Plus,
    Minus,
    Refresh
  },

  props: {
    sequence: {
      type: String,
      required: true
    }
  },

  data() {
    return {
      activeTab: 'sequence',
      currentZoom: 1,
      zoomTransform: null,
      svgElement: null,
      zoomBehavior: null,
      predictedStructure: []
    }
  },

  mounted() {
    if (this.activeTab === 'graph') {
      this.$nextTick(() => {
        this.drawProteinGraph()
      })
    }
    // 生成二级结构预测
    this.predictSecondaryStructure()
  },

  watch: {
    sequence() {
      if (this.activeTab === 'graph') {
        this.$nextTick(() => {
          this.drawProteinGraph()
        })
      }
      // 当序列变化时重新预测结构
      this.predictSecondaryStructure()
    }
  },

  methods: {
    getAminoAcidClass(aa) {
      const hydrophobic = ['A', 'I', 'L', 'M', 'F', 'W', 'V']
      const hydrophilic = ['S', 'T', 'N', 'Q']
      const positive = ['R', 'H', 'K']
      const negative = ['D', 'E']
      const special = ['C', 'G', 'P', 'Y']

      if (hydrophobic.includes(aa)) return 'hydrophobic'
      if (hydrophilic.includes(aa)) return 'hydrophilic'
      if (positive.includes(aa)) return 'positive'
      if (negative.includes(aa)) return 'negative'
      if (special.includes(aa)) return 'special'
      return ''
    },

    translateType(type) {
      const translations = {
        'hydrophobic': '疏水性',
        'hydrophilic': '亲水性',
        'positive': '正电荷',
        'negative': '负电荷',
        'special': '特殊'
      }
      return translations[type] || type
    },

    drawProteinGraph() {
      if (this.activeTab !== 'graph') return
      if (!this.sequence || this.sequence.length === 0) return

      const container = this.$refs.graphContainer
      const width = container.clientWidth
      const height = 300

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
      this.zoomBehavior = d3.zoom()
        .scaleExtent([0.1, 5])
        .on('zoom', (event) => {
          this.currentZoom = event.transform.k
          g.attr('transform', event.transform)
        })

      // 保存引用以供控制按钮使用
      this.svgElement = svg.node()
      svg.call(this.zoomBehavior)

      // 创建节点数据
      const nodes = Array.from(this.sequence).map((aa, i) => ({
        id: i,
        aa: aa,
        group: this.getAminoAcidClass(aa),
        x: width / 2 + (Math.cos(i * 2 * Math.PI / this.sequence.length) * width / 3 * Math.min(1, 30 / this.sequence.length)),
        y: height / 2 + (Math.sin(i * 2 * Math.PI / this.sequence.length) * height / 3 * Math.min(1, 30 / this.sequence.length))
      }))

      // 创建连线数据（相邻氨基酸之间的连接）
      const links = Array.from({ length: this.sequence.length - 1 }, (_, i) => ({
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
        .call(this.drag(simulation))

      // 为节点组添加提示信息
      nodeGroups.append('title')
        .text(d => `${d.aa} (位置: ${d.id + 1}, 类型: ${this.translateType(d.group)})`)

      // 绘制节点圆圈
      nodeGroups.append('circle')
        .attr('r', 8)
        .attr('fill', d => this.getNodeColor(d.group))
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
    },

    getNodeColor(group) {
      const colors = {
        'hydrophobic': '#ff7f7f',
        'hydrophilic': '#7fbfff',
        'positive': '#7fff7f',
        'negative': '#ff7fff',
        'special': '#ffff7f'
      }
      return colors[group] || '#ccc'
    },

    drag(simulation) {
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
    },

    zoomIn() {
      if (!this.svgElement || !this.zoomBehavior) return
      d3.select(this.svgElement)
        .transition()
        .duration(300)
        .call(this.zoomBehavior.scaleBy, 1.2)
    },

    zoomOut() {
      if (!this.svgElement || !this.zoomBehavior) return
      d3.select(this.svgElement)
        .transition()
        .duration(300)
        .call(this.zoomBehavior.scaleBy, 0.8)
    },

    resetZoom() {
      if (!this.svgElement || !this.zoomBehavior) return
      d3.select(this.svgElement)
        .transition()
        .duration(500)
        .call(this.zoomBehavior.transform, d3.zoomIdentity)
    },

    handleTabChange() {
      if (this.activeTab === 'graph') {
        this.$nextTick(() => {
          this.drawProteinGraph()
        })
      }
    },

    predictSecondaryStructure() {
      if (!this.sequence || this.sequence.length === 0) {
        this.predictedStructure = []
        return
      }

      // 初始化预测结构
      this.predictedStructure = new Array(this.sequence.length).fill('C') // 默认为无规卷曲

      // 氨基酸倾向性数据
      const helixPropensity = {
        'A': 1.4, 'L': 1.2, 'M': 1.2, 'E': 1.5, 'Q': 1.3, 'K': 1.2,
        'R': 1.1, 'H': 1.0, 'I': 0.9, 'W': 0.8, 'V': 0.9, 'F': 0.9,
        'Y': 0.7, 'D': 0.8, 'N': 0.7, 'T': 0.7, 'S': 0.7, 'G': 0.4,
        'P': 0.3, 'C': 0.9
      }

      const sheetPropensity = {
        'V': 1.9, 'I': 1.8, 'Y': 1.6, 'F': 1.5, 'W': 1.4, 'T': 1.2,
        'C': 1.2, 'L': 1.1, 'M': 1.0, 'A': 0.7, 'R': 0.8, 'G': 0.6,
        'D': 0.5, 'K': 0.7, 'S': 0.8, 'H': 0.9, 'N': 0.7, 'Q': 0.8,
        'P': 0.3, 'E': 0.5
      }

      // 滑动窗口预测二级结构
      const windowSize = 5

      for (let i = 0; i <= this.sequence.length - windowSize; i++) {
        const window = this.sequence.slice(i, i + windowSize)

        // 计算窗口内平均螺旋和折叠倾向性
        let helixScore = 0
        let sheetScore = 0

        for (const aa of window) {
          helixScore += helixPropensity[aa] || 0.5
          sheetScore += sheetPropensity[aa] || 0.5
        }

        helixScore /= windowSize
        sheetScore /= windowSize

        // 根据阈值判定结构
        const threshold = 1.1

        // 更新中心位置的结构
        const center = i + Math.floor(windowSize / 2)

        if (helixScore > threshold && helixScore > sheetScore) {
          this.predictedStructure[center] = 'H'
        } else if (sheetScore > threshold && sheetScore > helixScore) {
          this.predictedStructure[center] = 'E'
        }
      }

      // 平滑结构预测（合并相邻同类结构）
      this.smoothStructurePrediction()
    },

    smoothStructurePrediction() {
      // 排除过短的结构段（少于3个残基）
      for (let i = 1; i < this.sequence.length - 1; i++) {
        if (this.predictedStructure[i-1] !== this.predictedStructure[i] &&
            this.predictedStructure[i] !== this.predictedStructure[i+1]) {
          this.predictedStructure[i] = this.predictedStructure[i-1]
        }
      }

      // 合并短间隔的相同结构
      for (let i = 2; i < this.sequence.length - 2; i++) {
        if (this.predictedStructure[i-2] === this.predictedStructure[i+2] &&
            this.predictedStructure[i-2] !== 'C') {
          this.predictedStructure[i-1] = this.predictedStructure[i-2]
          this.predictedStructure[i] = this.predictedStructure[i-2]
          this.predictedStructure[i+1] = this.predictedStructure[i-2]
        }
      }
    },

    getStructureClass(struct) {
      switch (struct) {
        case 'H': return 'helix'
        case 'E': return 'sheet'
        case 'C': return 'coil'
        default: return ''
      }
    },

    getStructureTitle(struct) {
      switch (struct) {
        case 'H': return 'α螺旋 (Alpha Helix)'
        case 'E': return 'β折叠 (Beta Sheet)'
        case 'C': return '无规卷曲 (Random Coil)'
        default: return '未知结构'
      }
    }
  }
}
</script>

<style scoped>
.protein-viz-container {
  margin: 10px 0;
  padding: 10px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.sequence-view {
  padding: 10px;
}

.sequence-container {
  font-family: monospace;
  line-height: 1.8;
  word-break: break-all;
}

.aa-residue {
  padding: 2px;
  margin: 1px;
  border-radius: 3px;
  cursor: pointer;
}

.hydrophobic { background-color: #ff7f7f; }
.hydrophilic { background-color: #7fbfff; }
.positive { background-color: #7fff7f; }
.negative { background-color: #ff7fff; }
.special { background-color: #ffff7f; }

.legend {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.color-box {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.graph-container {
  height: 300px;
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.graph-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.zoom-level {
  font-size: 12px;
  color: #606266;
  margin-left: 10px;
}

.graph-legend {
  margin-top: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.graph-note {
  font-size: 12px;
  color: #606266;
  margin: 5px 0;
  font-style: italic;
}

/* 二级结构预测样式 */
.structure-view {
  padding: 10px;
}

.prediction-info {
  margin-bottom: 15px;
}

.structure-container {
  font-family: monospace;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  background-color: #f8f9fa;
}

.sequence-line, .structure-line {
  display: flex;
  flex-wrap: wrap;
  line-height: 1.8;
}

.structure-aa, .structure-symbol {
  width: 16px;
  text-align: center;
  margin: 1px;
}

.structure-symbol {
  border-radius: 2px;
  font-weight: bold;
}

.helix {
  background-color: #ff9999;
  color: #d32f2f;
}

.sheet {
  background-color: #99ccff;
  color: #1976d2;
}

.coil {
  background-color: #f0f0f0;
  color: #757575;
}

.structure-legend {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.structure-box {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  display: inline-block;
}
</style>