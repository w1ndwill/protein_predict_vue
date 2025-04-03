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
              <el-button @click="zoomIn" size="small" title="放大">
                <el-icon><Plus /></el-icon>
              </el-button>
              <el-button @click="zoomOut" size="small" title="缩小">
                <el-icon><Minus /></el-icon>
              </el-button>
              <el-button @click="resetZoom" size="small" title="重置视图">
                <el-icon><Refresh /></el-icon>
              </el-button>
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
import { getAminoAcidClass, getStructureClass, getStructureTitle } from '../utils/proteinUtils'
import { drawProteinGraph, zoomSvg, resetZoomSvg } from '../services/proteinVisualizationService'
import { predictSecondaryStructure } from '../services/structurePredictionService'

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
    this.updateStructurePrediction()
  },

  watch: {
    sequence() {
      if (this.activeTab === 'graph') {
        this.$nextTick(() => {
          this.drawProteinGraph()
        })
      }
      // 当序列变化时重新预测结构
      this.updateStructurePrediction()
    }
  },

  methods: {
    getAminoAcidClass,
    getStructureClass,
    getStructureTitle,

    updateStructurePrediction() {
      this.predictedStructure = predictSecondaryStructure(this.sequence)
    },

    drawProteinGraph() {
      if (this.activeTab !== 'graph') return
      if (!this.sequence || this.sequence.length === 0) return

      const container = this.$refs.graphContainer
      const width = container.clientWidth
      const height = 300

      const { svg, zoomBehavior } = drawProteinGraph(container, this.sequence, width, height, {
        onZoom: (zoom) => {
          this.currentZoom = zoom
        }
      })

      // 保存引用以供控制按钮使用
      this.svgElement = svg.node()
      this.zoomBehavior = zoomBehavior
    },

    zoomIn() {
      zoomSvg(this.svgElement, this.zoomBehavior, 1.2)
    },

    zoomOut() {
      zoomSvg(this.svgElement, this.zoomBehavior, 0.8)
    },

    resetZoom() {
      resetZoomSvg(this.svgElement, this.zoomBehavior)
    },

    handleTabChange() {
      if (this.activeTab === 'graph') {
        this.$nextTick(() => {
          this.drawProteinGraph()
        })
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