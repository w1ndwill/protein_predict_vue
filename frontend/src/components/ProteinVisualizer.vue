<template>
  <div class="protein-viz-container">
    <el-tabs v-model="activeTab" class="viz-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="序列浏览器" name="sequence">
        <div class="sequence-view">
          <div class="controls">
            <el-switch
              v-model="showFunctionalSites"
              active-text="显示功能位点"
              @change="updateFunctionalSites"
            />
          </div>

          <div class="sequence-display-wrapper">
            <div class="sequence-ruler">
              <span v-for="i in Math.ceil(sequence.length / 10)" :key="i" class="ruler-mark">
                {{ i * 10 }}
              </span>
            </div>
            <div class="sequence-container">
              <el-tooltip
                v-for="(aa, i) in sequence"
                :key="i"
                placement="top"
                effect="dark"
                :content="getAATitle(i, aa)"
                :open-delay="300"
              >
                <span :class="['aa-residue', getAminoAcidClass(aa)]">
                  {{ aa }}
                  <span v-if="showFunctionalSites" :class="['site-marker', getSiteClass(i)]"></span>
                </span>
              </el-tooltip>
            </div>
          </div>

          <div class="legend-grid">
            <div class="legend-group">
              <h4 class="legend-title">氨基酸类型</h4>
              <div class="legend">
                <div class="legend-item"><div class="color-box hydrophobic"></div>疏水性</div>
                <div class="legend-item"><div class="color-box hydrophilic"></div>亲水性</div>
                <div class="legend-item"><div class="color-box positive"></div>正电荷</div>
                <div class="legend-item"><div class="color-box negative"></div>负电荷</div>
                <div class="legend-item"><div class="color-box special"></div>特殊</div>
              </div>
            </div>
            <div v-if="showFunctionalSites" class="legend-group">
              <h4 class="legend-title">功能位点</h4>
              <div class="legend">
                <div class="legend-item"><div class="color-box active-site-legend"></div>活性位点</div>
                <div class="legend-item"><div class="color-box binding-site-legend"></div>结合位点</div>
                <div class="legend-item"><div class="color-box ptm-site-legend"></div>修饰位点</div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="二级结构" name="structure">
         <div class="structure-view">
          <div class="structure-stats-container">
             <div v-for="stat in structureStats" :key="stat.type" class="stat-card">
                <div class="stat-header">
                  <span class="stat-label">{{ stat.name }}</span>
                  <span class="stat-percentage">{{ stat.percentage.toFixed(1) }}%</span>
                </div>
                <el-progress :percentage="stat.percentage" :color="stat.color" :show-text="false" :stroke-width="10" />
             </div>
          </div>
          <div class="sequence-with-structure">
            <el-tooltip v-for="(aa, i) in sequence" :key="i" placement="top" effect="dark" :content="`${aa}${i+1}: ${getStructureName(secondaryStructure[i])}`">
              <span :class="['aa-struct-residue', getStructureClass(secondaryStructure[i])]">
                {{ aa }}
              </span>
            </el-tooltip>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="图拓扑结构" name="graph">
        <div class="graph-view">
          <div class="controls">
            <el-button-group>
              <el-button size="small" @click="zoomIn">放大</el-button>
              <el-button size="small" @click="zoomOut">缩小</el-button>
              <el-button size="small" @click="resetZoom">重置</el-button>
            </el-button-group>
            <span class="zoom-display">当前缩放: {{ (currentZoom * 100).toFixed(0) }}%</span>
          </div>
          <div ref="graphContainer" class="graph-container"></div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { getAminoAcidClass } from '@/utils/proteinUtils';
import { predictSecondaryStructure } from '@/services/structurePredictionService';
import { fetchFunctionalSites } from '@/services/functionalSitesService';
import { drawProteinGraph, zoomSvg, resetZoomSvg } from '@/services/proteinVisualizationService';

export default {
  name: 'ProteinVisualizer',
  props: {
    sequence: { type: String, required: true },
    proteinId: { type: String, default: '' }
  },
  setup(props) {
    const activeTab = ref('sequence');
    const showFunctionalSites = ref(true);
    const functionalSites = ref([]);
    const secondaryStructure = ref([]);
    
    // Graph state
    const graphContainer = ref(null);
    const graphSvg = ref(null);
    const graphZoomBehavior = ref(null);
    const currentZoom = ref(1);

    const updateFunctionalSites = async () => {
      if (!showFunctionalSites.value || !props.sequence) {
        functionalSites.value = [];
        return;
      }
      try {
        const response = await fetchFunctionalSites(props.sequence, props.proteinId);
        functionalSites.value = response.sites || [];
      } catch (error) {
        console.error('Failed to load functional sites:', error);
        functionalSites.value = [];
      }
    };

    const updateSecondaryStructure = () => {
      if (props.sequence) {
        secondaryStructure.value = predictSecondaryStructure(props.sequence);
      } else {
        secondaryStructure.value = [];
      }
    };

    const initGraphView = () => {
      if (!props.sequence || !graphContainer.value) return;
      const { svg, g, zoomBehavior } = drawProteinGraph(
        graphContainer.value,
        props.sequence,
        graphContainer.value.clientWidth,
        500,
        { onZoom: (zoom) => { currentZoom.value = zoom; } },
        { secondaryStructure: secondaryStructure.value, functionalSites: functionalSites.value }
      );
      graphSvg.value = svg;
      graphZoomBehavior.value = zoomBehavior;
    };

    const handleTabChange = (tab) => {
      if (tab.paneName === 'graph') {
        nextTick(() => {
          initGraphView();
        });
      }
    };
    
    watch(() => props.sequence, () => {
      updateSecondaryStructure();
      updateFunctionalSites();
      if (activeTab.value === 'graph') {
        nextTick(() => initGraphView());
      }
    }, { immediate: true });

    const getSiteClass = (position) => {
      const site = functionalSites.value.find(s => position >= s.position && position < s.position + s.length);
      return site ? site.type : '';
    };

    const getAATitle = (position, aa) => {
      let title = `${aa} (位置: ${position + 1})`;
      const site = functionalSites.value.find(s => position >= s.position && position < s.position + s.length);
      if (site) {
        title += `\n位点: ${site.description}`;
      }
      return title;
    };

    const getStructureClass = (structType) => `struct-${structType}`;
    const getStructureName = (structType) => ({ H: 'α-螺旋', E: 'β-折叠', C: '无规卷曲' }[structType] || '');

    const structureStats = computed(() => {
      const total = secondaryStructure.value.length;
      if (total === 0) return [];
      const counts = secondaryStructure.value.reduce((acc, type) => {
        acc[type] = (acc[type] || 0) + 1;
        return acc;
      }, {});

      return [
        { type: 'H', name: 'α-螺旋', percentage: ((counts.H || 0) / total) * 100, color: '#F56565' },
        { type: 'E', name: 'β-折叠', percentage: ((counts.E || 0) / total) * 100, color: '#4299E1' },
        { type: 'C', name: '无规卷曲', percentage: ((counts.C || 0) / total) * 100, color: '#A0AEC0' }
      ];
    });

    return {
      activeTab,
      showFunctionalSites,
      functionalSites,
      secondaryStructure,
      structureStats,
      graphContainer,
      currentZoom,
      updateFunctionalSites,
      getAminoAcidClass,
      getSiteClass,
      getAATitle,
      getStructureClass,
      getStructureName,
      handleTabChange,
      zoomIn: () => zoomSvg(graphSvg.value, graphZoomBehavior.value, 1.2),
      zoomOut: () => zoomSvg(graphSvg.value, graphZoomBehavior.value, 0.8),
      resetZoom: () => resetZoomSvg(graphSvg.value, graphZoomBehavior.value),
    };
  }
};
</script>

<style scoped>
/* --- General Container & Tabs --- */
.protein-viz-container {
  margin-top: 2rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-large);
  background-color: var(--color-background-soft);
  padding: 0.5rem;
  box-shadow: var(--shadow-sm);
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav) {
  border: none !important;
}

:deep(.el-tabs__item) {
  padding: 0 20px;
  height: 50px;
  font-weight: 500;
  color: var(--color-text-mute);
}

:deep(.el-tabs__item.is-active) {
  color: var(--color-primary);
}

:deep(.el-tabs__active-bar) {
  background-color: var(--color-primary);
  height: 3px;
}

:deep(.el-tab-pane) {
  padding: 1.5rem;
}

.controls {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-background);
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius-medium);
}

/* --- Sequence Viewer --- */
.sequence-display-wrapper {
  position: relative;
  padding: 1rem;
  background-color: var(--color-background);
  border-radius: var(--border-radius-medium);
}

.sequence-ruler {
  display: flex;
  margin-bottom: 0.5rem;
  padding-left: 1.5em; /* Align with sequence */
}

.ruler-mark {
  flex: 0 0 calc(1.5em * 10); /* 10 residues per mark */
  font-size: 0.75rem;
  color: var(--color-text-mute);
  position: relative;
}
.ruler-mark::before {
  content: '|';
  position: absolute;
  left: 0;
}

.sequence-container {
  font-family: 'Fira Code', monospace;
  line-height: 1.5;
  word-break: break-all;
}

.aa-residue {
  display: inline-block;
  width: 1.5em;
  height: 1.5em;
  line-height: 1.5em;
  text-align: center;
  border-radius: var(--border-radius-small);
  font-weight: 500;
  cursor: pointer;
  position: relative;
  margin: 1px;
  transition: all 0.2s ease-in-out;
}
.aa-residue:hover {
  transform: scale(1.2);
  z-index: 10;
}

/* Amino Acid Type Colors */
.hydrophobic { background-color: #FEF3C7; color: #92400E; }
.hydrophilic { background-color: #D1FAE5; color: #065F46; }
.positive { background-color: #DBEAFE; color: #1E40AF; }
.negative { background-color: #FEE2E2; color: #991B1B; }
.special { background-color: #E5E7EB; color: #1F2937; }

/* Site Marker Styles */
.site-marker {
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 3px;
  border-radius: 2px;
}
.site-marker.active-site { background-color: #F56565; }
.site-marker.binding-site { background-color: #4299E1; }
.site-marker.ptm-site { background-color: #48BB78; }

/* --- Legend --- */
.legend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}
.legend-group {
  background-color: var(--color-background);
  padding: 1rem;
  border-radius: var(--border-radius-medium);
}
.legend-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-heading);
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.legend-item {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
}
.color-box {
  width: 14px;
  height: 14px;
  margin-right: 8px;
  border-radius: 3px;
}
.color-box.active-site-legend { background-color: #F56565; }
.color-box.binding-site-legend { background-color: #4299E1; }
.color-box.ptm-site-legend { background-color: #48BB78; }

/* --- Secondary Structure View --- */
.structure-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.structure-stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.stat-card {
  background-color: var(--color-background);
  padding: 1rem;
  border-radius: var(--border-radius-medium);
}
.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
}
.stat-label {
  font-weight: 600;
  color: var(--color-heading);
}
.stat-percentage {
  font-family: 'Fira Code', monospace;
  font-weight: 500;
  color: var(--color-text);
}
.sequence-with-structure {
  background-color: var(--color-background);
  padding: 1rem;
  border-radius: var(--border-radius-medium);
  font-family: 'Fira Code', monospace;
  line-height: 1.8;
  word-break: break-all;
}
.aa-struct-residue {
  display: inline-block;
  padding: 0 0.2em;
  border-radius: 2px;
  cursor: pointer;
}
.struct-H { background-color: rgba(245, 101, 101, 0.3); }
.struct-E { background-color: rgba(66, 153, 225, 0.3); }
.struct-C { background-color: rgba(226, 232, 240, 0.5); }

/* --- Graph View --- */
.graph-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.graph-container {
  height: 500px;
  background-color: var(--color-background);
  border-radius: var(--border-radius-medium);
  border: 1px solid var(--color-border);
  position: relative;
}
.zoom-display {
  font-family: 'Fira Code', monospace;
  color: var(--color-text-mute);
}
</style>
