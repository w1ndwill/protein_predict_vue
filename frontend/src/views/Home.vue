<template>
  <div class="app-container">
    <!-- 顶栏 -->
    <Navbar :showBackButton="true" />
    <div class="page-content">
      <div class="home-container">
        <div class="header-section">
          <h1 class="main-title">蛋白质功能预测系统</h1>
          <p class="subtitle">选择预测模式并输入数据进行蛋白质功能预测分析</p>
        </div>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-card shadow="hover" class="mode-card">
              <!-- 预测模式选择 -->
              <div class="mode-selection">
                <el-radio-group v-model="predictionMode" size="large">
                  <el-radio-button label="fasta">FASTA文件预测</el-radio-button>
                  <el-radio-button label="sequence">序列直接预测</el-radio-button>
                </el-radio-group>
              </div>

              <!-- FASTA文件上传模式 -->
              <file-uploader
                v-if="predictionMode === 'fasta'"
                :loading="predicting"
                @success="handleSuccess"
                @error="handleError"
              />

              <!-- 序列输入模式 -->
              <sequence-input
                v-else
                :loading="predicting"
                @update:sequence="sequence = $event"
                @submit="predictSequence"
              />
            </el-card>
          </el-col>
        </el-row>

        <!-- 预测结果展示 -->
        <el-row :gutter="20" v-if="predictionResults.length > 0" class="result-section">
          <el-col :span="24">
            <el-card shadow="hover" class="result-card">
              <template #header>
                <div class="section-header">
                  <h2>当前预测结果</h2>
                  <span class="current-file" v-if="currentFileName">{{ currentFileName }}</span>
                </div>
              </template>

              <!-- 蛋白质列表（FASTA结果） -->
              <protein-list
                v-if="isFastaResult"
                :proteins="proteinOptions"
                :selected-id="selectedProteinId"
                :sequences="proteinSequences"
                @select="handleProteinChange"
              />

              <!-- 当选择了蛋白质时显示其预测结果 -->
              <div v-if="selectedProteinId || !isFastaResult">
                <h3 v-if="selectedProteinId" class="selected-protein">
                  当前选择: {{ selectedProteinId }}
                </h3>

                <prediction-table :results="filteredResults" />

                <!-- 添加蛋白质可视化组件 -->
                <protein-visualizer
                  v-if="sequence"
                  :sequence="sequence"
                  class="visualizer-section"
                />

                <!-- 序列长度信息 -->
                <div v-if="sequence" class="sequence-info">
                  <el-tag type="info">序列长度: {{ sequence.length }}</el-tag>
                </div>
              </div>

              <div v-else-if="isFastaResult" class="no-protein-selected">
                <el-alert
                  title="请从上方列表中选择一个蛋白质查看详细结果"
                  type="info"
                  :closable="false"
                  center
                  show-icon
                />
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 历史记录 -->
        <history-table
          :records="historyRecords"
          :loading="loadingHistory"
          @refresh="loadHistory"
          @view-result="viewHistoryResult"
        />
      </div>
    </div>
  </div>
</template>

<script>
import PredictionTable from '../components/PredictionTable.vue'
import ProteinVisualizer from '../components/ProteinVisualizer.vue'
import Navbar from '../components/Navbar.vue'
import FileUploader from '../components/Home/FileUploader.vue'
import SequenceInput from '../components/Home/SequenceInput.vue'
import ProteinList from '../components/Home/ProteinList.vue'
import HistoryTable from '../components/Home/HistoryTable.vue'
import { predictFromSequence, getHistoryRecords, getHistoryResult, getProteinData } from '@/services/proteinApi'
import { isMultiProteinResult, getProteinOptions } from '@/utils/proteinUtils'

export default {
  name: 'Home',
  components: {
    PredictionTable,
    ProteinVisualizer,
    Navbar,
    FileUploader,
    SequenceInput,
    ProteinList,
    HistoryTable
  },

  data() {
    return {
      predictionMode: 'fasta',
      sequence: '',
      predicting: false,
      predictionResults: [],
      historyRecords: [],
      loadingHistory: false,
      currentFileName: '',
      selectedProteinId: '',
      isFastaResult: false,
      // 存储蛋白质序列信息
      proteinSequences: {}
    }
  },

  computed: {
    proteinOptions() {
      return getProteinOptions(this.predictionResults)
    },

    filteredResults() {
      if (!this.selectedProteinId) {
        return this.predictionResults
      }
      return this.predictionResults.filter(r => r.protein_id === this.selectedProteinId)
    }
  },

  mounted() {
    // 页面加载时就获取历史记录
    this.loadHistory()
  },

  methods: {
    async predictSequence(sequence) {
      if (!sequence) {
        this.$message.warning('请输入蛋白质序列')
        return
      }

      this.predicting = true
      try {
        const response = await predictFromSequence(sequence)
        this.handleSuccess(response.data)
      } catch (error) {
        this.handleError(error)
      } finally {
        this.predicting = false
      }
    },

    handleSuccess(response) {
      this.predictionResults = response.results
      this.currentFileName = response.filename

      // 判断是否为FASTA结果
      this.isFastaResult = isMultiProteinResult(response.results)

      // 存储蛋白质序列信息
      this.storeProteinSequences(response.results)

      if (this.isFastaResult && response.results.length > 0) {
        // 对于FASTA文件，默认选择第一个蛋白质
        const firstProteinId = [...new Set(response.results.map(r => r.protein_id))][0]
        this.selectedProteinId = firstProteinId
        this.sequence = this.getProteinSequence(firstProteinId)
      } else {
        // 对于单序列预测，直接使用该序列
        this.sequence = response.results.length > 0 ? response.results[0].sequence : '';
        this.selectedProteinId = response.results.length > 0 ? response.results[0].protein_id : '';
      }

      this.$message.success('预测完成')
      this.loadHistory()
    },

    storeProteinSequences(results) {
      // 存储每个蛋白质ID对应的序列
      results.forEach(result => {
        if (result.protein_id && result.sequence) {
          this.proteinSequences[result.protein_id] = result.sequence
        }
      })
    },

    getProteinSequence(proteinId) {
      // 从存储的序列中获取
      return this.proteinSequences[proteinId] || ''
    },

    async handleProteinChange(proteinId) {
      if (!proteinId || !this.currentFileName) return

      this.selectedProteinId = proteinId

      // 先尝试从本地存储获取序列
      const localSequence = this.getProteinSequence(proteinId)
      if (localSequence) {
        this.sequence = localSequence
        return
      }

      // 如果本地没有，则从后端获取
      try {
        const response = await getProteinData(proteinId, this.currentFileName)
        if (response.data.sequence) {
          this.sequence = response.data.sequence
          // 存储到本地缓存
          this.proteinSequences[proteinId] = response.data.sequence
        }
      } catch (error) {
        this.$message.error('获取蛋白质序列失败：' + error.message)
      }
    },

    handleError(error) {
      this.$message.error('预测失败：' + (error.response?.data?.error || error.message))
      this.predictionResults = []
    },

    async loadHistory() {
      this.loadingHistory = true
      try {
        const response = await getHistoryRecords()
        this.historyRecords = response.data
      } catch (error) {
        this.$message.error('加载历史记录失败：' + error.message)
        this.historyRecords = []
      } finally {
        this.loadingHistory = false
      }
    },

    async viewHistoryResult(record) {
      try {
        const response = await getHistoryResult(record.filename)
        this.predictionResults = response.data
        this.currentFileName = record.filename

        // 判断是否为FASTA结果
        this.isFastaResult = isMultiProteinResult(response.data)

        // 存储蛋白质序列信息
        this.storeProteinSequences(response.data)

        if (this.isFastaResult && response.data.length > 0) {
          // 对于FASTA文件，默认选择第一个蛋白质
          const firstProteinId = [...new Set(response.data.map(r => r.protein_id))][0]
          this.selectedProteinId = firstProteinId
          this.sequence = this.getProteinSequence(firstProteinId)
        } else {
          // 对于单序列预测，直接使用该序列
          this.sequence = response.data[0]?.sequence || ''
        }

        // 滚动到结果部分
        this.$nextTick(() => {
          const resultElem = document.querySelector('.result-section')
          resultElem?.scrollIntoView({ behavior: 'smooth' })
        })

      } catch (error) {
        this.$message.error('加载历史结果失败：' + error.message)
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/styles/home.css';
</style>