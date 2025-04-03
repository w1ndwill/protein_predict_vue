<template>
  <div class="prediction-table-container">
    <el-table
      :data="sortedResults"
      style="width: 100%"
      :header-cell-style="headerStyle"
      border
      stripe
      v-loading="loading"
    >

      <el-table-column prop="function" label="预测功能" min-width="70%">
        <template #default="scope">
          <div class="function-cell">
            <span class="function-name">{{ scope.row.function }}</span>
            <div class="function-desc">{{ getFunctionDescription(scope.row.function) }}</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="confidence" label="置信度" min-width="30%">
        <template #default="scope">
          <div class="confidence-cell">
            <div class="confidence-value">{{ (scope.row.confidence * 100).toFixed(1) }}%</div>
            <el-progress
              :percentage="scope.row.confidence * 100"
              :stroke-width="10"
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
    results: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      headerStyle: {
      background: '#f2f6fc',
      color: '#303133',
      fontWeight: '600',
      padding: '12px 0',
      borderBottom: '2px solid #DCDFE6'
      },
      // GO功能描述映射
      functionDescriptions: {
        'protein_binding': '蛋白质结合能力，通过特定结构域与其他蛋白质形成复合物或相互作用网络，参与信号传导、代谢调控、免疫反应等多种生物学过程',
        'dna_binding': 'DNA结合能力，通过锌指、螺旋-转角-螺旋等结构特异性识别并结合DNA序列，调控基因表达、DNA复制、修复和重组等核心生物学过程',
        'catalytic': '催化功能，作为酶分子提供活性位点，降低化学反应活化能，加速生物体内各类代谢反应，包括水解、氧化还原、转移等反应类型',
        'structural': '结构功能，提供细胞骨架支撑、组织完整性维持或形成大分子复合物的框架结构，如微管蛋白、胶原蛋白等，确保细胞和组织的形态与力学特性',
        'transcription': '转录相关功能，作为转录因子或转录复合物组分，识别启动子或增强子序列，调控RNA合成速率，决定基因表达的时空特异性',
        'signal': '信号传导功能，参与细胞内外信号的接收、转导和放大，包括受体活化、第二信使产生、蛋白质修饰级联，最终影响细胞命运决定和应激响应',
        'transport': '运输功能，作为载体蛋白、通道蛋白或泵蛋白，介导离子、小分子、大分子等物质跨膜转运或细胞内区室间的定向运输，维持细胞内环境稳态',
        'enzyme_regulation': '酶调节功能，通过与酶分子的可逆结合或共价修饰，改变酶的构象、活性位点可及性或底物亲和力，精确调控代谢途径通量和酶活性'
      }
    }
  },
  computed: {
    sortedResults() {
      return [...this.results].sort((a, b) => b.confidence - a.confidence)
    }
  },
  methods: {
    getFunctionDescription(func) {
      return this.functionDescriptions[func] || '未知功能'
    },
    getConfidenceColor(confidence) {
      if (confidence >= 0.8) return '#67C23A';
      if (confidence >= 0.6) return '#85ce61';
      if (confidence >= 0.4) return '#E6A23C';
      if (confidence >= 0.2) return '#f89b29';
      return '#F56C6C';
    }
  }
}
</script>

<style scoped>
.prediction-table-container {
  margin: 20px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.function-cell {
  display: flex;
  flex-direction: column;
  padding: 10px 0;
}

.function-name {
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 6px;
  font-family: "Source Sans Pro", "Microsoft YaHei", sans-serif;
  font-size: 15px;
  letter-spacing: 0.3px;
}

.function-desc {
  font-size: 13px;
  color: #5c6b7a;
  line-height: 1.5;
  font-family: "Noto Sans SC", sans-serif;
  text-align: justify;
  padding-right: 8px;
  text-indent: 0.5em;
  position: relative;
}

.function-desc::before {
  content: "";
  position: absolute;
  left: -8px;
  top: 6px;
  width: 3px;
  height: calc(100% - 12px);
  background-color: #e8eaec;
  border-radius: 2px;
}

.confidence-cell {
  padding: 12px 0;
}

.confidence-value {
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
  text-align: center;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 16px;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

:deep(.el-table) {
  border-radius: 6px;
}

:deep(.el-table__row) {
  height: auto;
  min-height: 60px;
}

:deep(.el-table__header-wrapper th) {
  padding: 12px 0;
  font-size: 14px;
}

:deep(.el-progress-bar__outer) {
  border-radius: 4px;
  background-color: #ebeef5;
}

:deep(.el-progress-bar__inner) {
  border-radius: 4px;
  transition: width 0.6s ease;
}

:deep(.el-table__row:hover) {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  border-radius: 3px;
  background: #c0c4cc;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  border-radius: 3px;
  background: #ebeef5;
}
</style>