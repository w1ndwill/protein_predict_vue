<template>
  <div class="prediction-table-container">
    <el-table
      :data="sortedResults"
      style="width: 100%"
      :row-class-name="'table-row-custom'"
      v-loading="loading"
    >
      <el-table-column prop="function" label="预测功能" min-width="65%">
        <template #default="scope">
          <div class="function-cell">
            <el-tag :color="getFunctionColor(scope.row.function)" effect="dark" class="function-tag">
              {{ scope.row.function }}
            </el-tag>
            <div class="function-desc">{{ getFunctionDescription(scope.row.function) }}</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="confidence" label="置信度" min-width="35%">
        <template #default="scope">
          <div class="confidence-cell">
            <span class="confidence-value">{{ (scope.row.confidence * 100).toFixed(1) }}%</span>
            <el-progress
              :percentage="scope.row.confidence * 100"
              :stroke-width="12"
              :color="getConfidenceColor(scope.row.confidence)"
              :show-text="false"
            ></el-progress>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'PredictionTable',
  props: {
    results: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  data() {
    return {
      functionDescriptions: {
        'protein_binding': '与其他蛋白质形成复合物，参与信号传导、代谢调控等。',
        'dna_binding': '特异性识别并结合DNA序列，调控基因表达、复制和修复。',
        'catalytic': '作为酶，加速生物体内的化学反应，如水解、氧化还原等。',
        'structural': '提供细胞骨架支撑，维持组织完整性，确保细胞和组织的形态。',
        'transcription': '作为转录因子，调控RNA合成速率，决定基因表达的时空特异性。',
        'signal': '参与细胞内外信号的接收、转导和放大，影响细胞命运。',
        'transport': '介导离子、小分子等物质跨膜转运，维持细胞内环境稳态。',
        'enzyme_regulation': '通过与酶结合或修饰，精确调控代谢途径和酶活性。'
      },
      functionColors: {
        'protein_binding': '#805AD5', // Secondary color
        'dna_binding': '#38B2AC', // Primary color
        'catalytic': '#D53F8C', // A pink/magenta
        'structural': '#D69E2E', // A gold/yellow
        'transcription': '#3182CE', // A blue
        'signal': '#DD6B20', // An orange
        'transport': '#319795', // A darker teal
        'enzyme_regulation': '#5A67D8' // An indigo
      }
    }
  },
  computed: {
    sortedResults() {
      return [...this.results].sort((a, b) => b.confidence - a.confidence);
    }
  },
  methods: {
    getFunctionDescription(func) {
      return this.functionDescriptions[func] || '功能描述待补充。';
    },
    getConfidenceColor(confidence) {
      if (confidence >= 0.8) return 'var(--color-primary)';
      if (confidence >= 0.6) return 'var(--color-secondary)';
      if (confidence >= 0.4) return '#F6AD55'; // Orange
      return '#F56565'; // Red
    },
    getFunctionColor(func) {
      return this.functionColors[func] || '#718096'; // Muted grey for unknown
    }
  }
}
</script>

<style scoped>
.prediction-table-container {
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-large);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* Overriding Element Plus Table Styles */
:deep(.el-table) {
  --el-table-border-color: var(--color-border);
  --el-table-header-bg-color: var(--color-background);
  --el-table-header-text-color: var(--color-heading);
  --el-table-tr-bg-color: var(--color-background-soft);
  --el-table-row-hover-bg-color: var(--color-background-mute);
}

:deep(.el-table__header-wrapper th) {
  font-weight: 600;
  padding: 16px 12px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

:deep(.el-table__row) {
  transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
}

:deep(.el-table__row:hover) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  z-index: 10;
}

.function-cell {
  padding: 16px 8px;
}

.function-tag {
  border: none;
  font-weight: 600;
  margin-bottom: 8px;
  color: white !important; /* Ensure text is readable on dark tags */
}

.function-desc {
  font-size: 0.9rem;
  color: var(--color-text-mute);
  line-height: 1.6;
}

.confidence-cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
  padding: 16px 8px;
}

.confidence-value {
  font-weight: 700;
  color: var(--color-heading);
  margin-bottom: 8px;
  font-family: 'Fira Code', monospace;
  font-size: 1.1rem;
}

:deep(.el-progress-bar__outer) {
  border-radius: var(--border-radius-small);
  background-color: var(--color-background-mute);
}

:deep(.el-progress-bar__inner) {
  border-radius: var(--border-radius-small);
}
</style>
