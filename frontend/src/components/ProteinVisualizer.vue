<template>
  <div class="protein-viz-container">
    <el-tabs v-model="activeTab" @tab-click="handleTabChange">

      <el-tab-pane label="序列与功能位点" name="sequence">
        <div class="sequence-view">
          <!-- 控制面板：添加功能位点显示开关 -->
          <div class="controls">
            <el-switch
              v-model="showFunctionalSites"
              active-text="显示功能位点"
              inactive-text="隐藏功能位点"
              @change="updateFunctionalSites"
            />
          </div>

          <!-- 功能位点图例 - 仅在启用功能位点时显示 -->
          <div v-if="showFunctionalSites" class="functional-sites-legend">
            <div class="site-type active-site">活性位点</div>
            <div class="site-type binding-site">结合位点</div>
            <div class="site-type ptm-site">修饰位点</div>
          </div>

          <!-- 序列容器 -->
          <div class="sequence-container">
            <span
              v-for="(aa, i) in sequence"
              :key="i"
              :class="[
                'aa-residue',
                getAminoAcidClass(aa),
                showFunctionalSites ? getSiteClass(i) : ''
              ]"
              :title="getAATitle(i, aa)"
            >
              {{ aa }}
            </span>
          </div>

          <!-- 氨基酸类型图例 -->
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
              <span>正电荷 (KR)</span>
            </div>
            <div class="legend-item">
              <div class="color-box negative"></div>
              <span>负电荷 (DE)</span>
            </div>
            <div class="legend-item">
              <div class="color-box special"></div>
              <span>特殊 (CGP)</span>
            </div>
            <div class="legend-item">
              <div class="color-box aromatic"></div>
              <span>芳香族 (YH)</span>
            </div>
          </div>

          <!-- 功能位点详情列表 - 仅在有功能位点且显示功能位点时显示 -->
          <div v-if="showFunctionalSites && functionalSites.length > 0" class="sites-list">
            <h4>预测功能位点详情：</h4>
            <el-table :data="functionalSites" stripe style="width: 100%;" size="small">
              <el-table-column prop="description" label="位点描述" />
              <el-table-column label="位置">
                <template #default="scope">
                  {{ scope.row.position + 1 }} - {{ scope.row.position + scope.row.length }}
                </template>
              </el-table-column>
              <el-table-column label="类型">
                <template #default="scope">
                  <el-tag :type="getSiteTagType(scope.row.type)">
                    {{ getSiteTypeName(scope.row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else-if="showFunctionalSites && functionalSites.length === 0" class="no-sites">
            <el-alert title="未检测到功能位点" type="info" :closable="false" center />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="图拓扑结构" name="graph">
        <div class="graph-view">
          <div class="controls">
            <el-button-group>
              <el-button size="small" @click="zoomIn">
                <i class="el-icon-zoom-in"></i> 放大
              </el-button>
              <el-button size="small" @click="zoomOut">
                <i class="el-icon-zoom-out"></i> 缩小
              </el-button>
              <el-button size="small" @click="resetZoom">
                <i class="el-icon-refresh"></i> 重置
              </el-button>
            </el-button-group>
            <span class="zoom-display">当前缩放: {{ (currentZoom * 100).toFixed(0) }}%</span>
          </div>
          <div ref="graphContainer" class="graph-container"></div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="二级结构预测" name="structure">
        <div class="structure-view">
          <div class="structure-legend">
            <div class="structure-item alpha-helix">α-螺旋 (H)</div>
            <div class="structure-item beta-sheet">β-折叠 (E)</div>
            <div class="structure-item coil">无规卷曲 (C)</div>
          </div>
          <div class="sequence-with-structure">
            <span
              v-for="(aa, i) in sequence"
              :key="i"
              :class="['aa-residue', getAminoAcidClass(aa), getStructureClass(secondaryStructure[i])]"
              :title="`${aa} (位置: ${i+1}, 结构: ${getStructureName(secondaryStructure[i])})`"
            >
              {{ aa }}
            </span>
          </div>
          <div class="structure-info">
            <div class="structure-stats">
              <div class="stat-item">
                <div class="label">α-螺旋:</div>
                <div class="value">{{ getStructurePercent('H') }}%</div>
                <el-progress :percentage="getStructurePercent('H')" color="#ff7675" :show-text="false"></el-progress>
              </div>
              <div class="stat-item">
                <div class="label">β-折叠:</div>
                <div class="value">{{ getStructurePercent('E') }}%</div>
                <el-progress :percentage="getStructurePercent('E')" color="#74b9ff" :show-text="false"></el-progress>
              </div>
              <div class="stat-item">
                <div class="label">无规卷曲:</div>
                <div class="value">{{ getStructurePercent('C') }}%</div>
                <el-progress :percentage="getStructurePercent('C')" color="#b2bec3" :show-text="false"></el-progress>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { getAminoAcidClass } from '../utils/proteinUtils'
import { drawProteinGraph, zoomSvg, resetZoomSvg } from '../services/proteinVisualizationService'
import { predictSecondaryStructure } from '../services/structurePredictionService'
import { fetchFunctionalSites } from '../services/functionalSitesService'

export default {
  name: 'ProteinVisualizer',
  props: {
    sequence: {
      type: String,
      required: true
    },
    proteinId: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      activeTab: 'sequence',
      graphSvg: null,
      graphZoomBehavior: null,
      secondaryStructure: [],
      currentZoom: 1,
      showFunctionalSites: false,
      functionalSites: [],
      loadingSites: false
    }
  },
  watch: {
    sequence() {
      this.updateVisualizations()
    }
  },
  methods: {
    // 氨基酸类型相关
    getAminoAcidClass,

    // 功能位点相关方法
    async updateFunctionalSites() {
      if (!this.showFunctionalSites || !this.sequence) {
        this.functionalSites = []
        return
      }

      this.loadingSites = true
      try {
        const response = await fetchFunctionalSites(this.sequence, this.proteinId)
        this.functionalSites = response.sites || []
      } catch (error) {
        console.error('加载功能位点失败:', error)
        this.$message.error('加载功能位点失败')
        this.functionalSites = []
      } finally {
        this.loadingSites = false
      }
    },

    // 获取氨基酸位置的功能位点类别
    getSiteClass(position) {
      if (!this.functionalSites.length) return ''

      for (const site of this.functionalSites) {
        const endPos = site.position + site.length
        if (position >= site.position && position < endPos) {
          return site.type
        }
      }
      return ''
    },

    // 获取氨基酸提示信息
    getAATitle(position, aa) {
      let title = `${aa} (位置: ${position+1})`

      if (this.showFunctionalSites) {
        const siteClass = this.getSiteClass(position)
        if (siteClass) {
          // 查找位点描述
          const site = this.functionalSites.find(s =>
            position >= s.position && position < (s.position + s.length)
          )
          if (site) {
            title += `, ${this.getSiteTypeName(siteClass)}: ${site.description}`
          }
        }
      }

      return title
    },

    // 获取位点类型名称
    getSiteTypeName(type) {
      const types = {
        'active-site': '活性位点',
        'binding-site': '结合位点',
        'ptm-site': '修饰位点'
      }
      return types[type] || '未知位点'
    },

    // 获取位点标签类型
    getSiteTagType(type) {
      const types = {
        'active-site': 'danger',
        'binding-site': 'primary',
        'ptm-site': 'success'
      }
      return types[type] || 'info'
    },

    // 图拓扑结构相关方法
    initGraphView() {
      if (!this.sequence || !this.$refs.graphContainer) return

      const width = this.$refs.graphContainer.clientWidth
      const height = 500

      const callbacks = {
        onZoom: (zoom) => {
          this.currentZoom = zoom
        }
      }

      const { svg, g, zoomBehavior } = drawProteinGraph(
        this.$refs.graphContainer,
        this.sequence,
        width,
        height,
        callbacks
      )

      this.graphSvg = svg.node()
      this.graphZoomBehavior = zoomBehavior
    },

    zoomIn() {
      zoomSvg(this.graphSvg, this.graphZoomBehavior, 1.2)
    },

    zoomOut() {
      zoomSvg(this.graphSvg, this.graphZoomBehavior, 0.8)
    },

    resetZoom() {
      resetZoomSvg(this.graphSvg, this.graphZoomBehavior)
      this.currentZoom = 1
    },

    // 二级结构相关方法
    initSecondaryStructure() {
      if (!this.sequence) return
      this.secondaryStructure = predictSecondaryStructure(this.sequence)
    },

    getStructureClass(structType) {
      if (structType === 'H') return 'alpha-helix'
      if (structType === 'E') return 'beta-sheet'
      return 'coil'
    },

    getStructureName(structType) {
      if (structType === 'H') return 'α-螺旋'
      if (structType === 'E') return 'β-折叠'
      return '无规卷曲'
    },

    getStructurePercent(structType) {
      if (!this.secondaryStructure.length) return 0
      const count = this.secondaryStructure.filter(s => s === structType).length
      return Math.round((count / this.secondaryStructure.length) * 100)
    },

    // Tab切换处理
    handleTabChange(tab) {
      if (tab.name === 'graph' && !this.graphSvg) {
        this.$nextTick(() => {
          this.initGraphView()
        })
      }
    },

    // 更新所有可视化
    updateVisualizations() {
      // 重新计算二级结构
      this.initSecondaryStructure()

      // 如果当前在图表视图，重新初始化图表
      if (this.activeTab === 'graph') {
        this.$nextTick(() => {
          this.initGraphView()
        })
      }

      // 如果显示功能位点，重新加载功能位点
      if (this.showFunctionalSites) {
        this.updateFunctionalSites()
      }
    }
  },
  mounted() {
    this.initSecondaryStructure()

    if (this.activeTab === 'graph') {
      this.$nextTick(() => {
        this.initGraphView()
      })
    }
  }
}
</script>

<style scoped>
.protein-viz-container {
  margin: 15px 0;
  padding: 10px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

/* 序列视图样式 */
.sequence-view {
  padding: 10px;
}

.sequence-container {
  font-family: monospace;
  line-height: 1.8;
  word-break: break-all;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  margin-bottom: 15px;
}

.aa-residue {
  display: inline-block;
  width: 1.8em;
  height: 1.8em;
  text-align: center;
  margin: 2px;
  border-radius: 4px;
  font-weight: bold;
  transition: all 0.2s;
  position: relative;
}

.aa-residue:hover {
  transform: scale(1.2);
  z-index: 10;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* 氨基酸种类样式 */
.hydrophobic {
  background-color: #fdcb6e;
  color: #000;
}

.hydrophilic {
  background-color: #81ecec;
  color: #000;
}

.positive {
  background-color: #74b9ff;
  color: #fff;
}

.negative {
  background-color: #ff7675;
  color: #fff;
}

.special {
  background-color: #a29bfe;
  color: #fff;
}

.aromatic {
  background-color: #55efc4;
  color: #000;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin: 5px;
}

.color-box {
  width: 16px;
  height: 16px;
  margin-right: 5px;
  border-radius: 3px;
}

.color-box.hydrophobic {
  background-color: #fdcb6e;
}

.color-box.hydrophilic {
  background-color: #81ecec;
}

.color-box.positive {
  background-color: #74b9ff;
}

.color-box.negative {
  background-color: #ff7675;
}

.color-box.special {
  background-color: #a29bfe;
}

.color-box.aromatic {
  background-color: #55efc4;
}

/* 图结构视图样式 */
.graph-view {
  padding: 10px;
}

.graph-container {
  height: 500px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.zoom-display {
  font-family: 'JetBrains Mono', monospace;
  padding: 4px 8px;
  background-color: #ebeef5;
  border-radius: 4px;
  font-size: 14px;
}

/* 二级结构视图样式 */
.structure-view {
  padding: 10px;
}

.structure-legend {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.structure-item {
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 13px;
}

.alpha-helix {
  background-color: rgba(255, 118, 117, 0.2);
  border: 1px solid #ff7675;
  color: #c0392b;
}

.beta-sheet {
  background-color: rgba(116, 185, 255, 0.2);
  border: 1px solid #74b9ff;
  color: #2980b9;
}

.coil {
  background-color: rgba(178, 190, 195, 0.2);
  border: 1px solid #b2bec3;
  color: #636e72;
}

.sequence-with-structure {
  font-family: monospace;
  line-height: 1.8;
  word-break: break-all;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  margin-bottom: 15px;
}

.structure-info {
  margin-top: 20px;
}

.structure-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
  margin: 0 auto;
}

.stat-item {
  display: grid;
  grid-template-columns: 80px 50px 1fr;
  align-items: center;
  gap: 10px;
}

.stat-item .label {
  text-align: right;
  font-weight: 500;
}

.stat-item .value {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}

/* 功能位点视图样式 */
.functional-sites-legend {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin: 15px 0;
}

.site-type {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 13px;
  position: relative;
}

.site-type::before {
  content: "";
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 5px;
  border-radius: 50%;
}

.active-site {
  background-color: rgba(245, 108, 108, 0.1);
}

.active-site::before {
  background-color: #F56C6C;
}

.binding-site {
  background-color: rgba(64, 158, 255, 0.1);
}

.binding-site::before {
  background-color: #409EFF;
}

.ptm-site {
  background-color: rgba(103, 194, 58, 0.1);
}

.ptm-site::before {
  background-color: #67C23A;
}

/* 功能位点标记样式 - 使用边框和阴影不影响氨基酸背景色 */
.aa-residue.active-site {
  box-shadow: 0 0 0 2px #F56C6C;
  border-bottom: 2px solid #F56C6C;
}

.aa-residue.binding-site {
  box-shadow: 0 0 0 2px #409EFF;
  border-bottom: 2px solid #409EFF;
}

.aa-residue.ptm-site {
  box-shadow: 0 0 0 2px #67C23A;
  border-bottom: 2px solid #67C23A;
}

.sites-list {
  margin-top: 15px;
}

.sites-list h4 {
  margin-bottom: 10px;
  color: #606266;
  font-weight: 600;
}

.no-sites {
  margin: 20px 0;
  text-align: center;
}
</style>