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
            <div v-if="predictionMode === 'fasta'" class="upload-section">
              <el-upload
                class="upload-demo"
                drag
                action="/api/predict"
                accept=".fasta"
                name="file"
                :on-success="handleSuccess"
                :on-error="handleError"
                :show-file-list="true"
                :loading="predicting"
              >
                <el-icon class="upload-icon"><upload /></el-icon>
                <div class="upload-text">
                  <p class="primary-text">拖拽FASTA文件到此处</p>
                  <p class="secondary-text">或点击上传</p>
                </div>
              </el-upload>
            </div>

            <!-- 序列输入模式 -->
            <div v-else class="sequence-input-section">
              <el-input
                v-model="sequence"
                type="textarea"
                :rows="6"
                placeholder="请输入蛋白质序列..."
                :maxlength="1000"
                show-word-limit
              />

              <div class="button-container">
                <el-button
                  type="primary"
                  :loading="predicting"
                  @click="predictSequence"
                  class="predict-btn"
                >
                  预测功能
                </el-button>
              </div>
            </div>
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
            <div v-if="isFastaResult" class="protein-list-section">
              <h3>蛋白质列表</h3>
              <div class="protein-grid">
                <el-card
                  v-for="protein in proteinOptions"
                  :key="protein.value"
                  class="protein-card"
                  :class="{'active': selectedProteinId === protein.value}"
                  shadow="hover"
                  @click="handleProteinChange(protein.value)"
                >
                  <div class="protein-name">{{ protein.label }}</div>
                  <div class="protein-info">
                    <span class="protein-length">序列长度: {{ getProteinLength(protein.value) }}</span>
                  </div>
                  <div class="protein-actions">
                    <el-button size="small" type="primary" plain>查看详情</el-button>
                  </div>
                </el-card>
              </div>
            </div>

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
      <el-row :gutter="20" class="history-section">
        <el-col :span="24">
          <el-card shadow="hover" class="history-card">
            <template #header>
              <div class="section-header">
                <h2>历史预测记录</h2>
                <el-button size="small" type="primary" plain @click="loadHistory">刷新</el-button>
              </div>
            </template>
            <el-table
              :data="historyRecords"
              style="width: 100%"
              :header-cell-style="headerStyle"
              v-loading="loadingHistory"
            >
              <el-table-column prop="filename" label="文件名" min-width="220">
                <template #default="scope">
                  <span class="filename-text">{{ scope.row.filename }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="created_time" label="预测时间" width="180">
                <template #default="scope">
                  <span class="time-text">{{ scope.row.created_time }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="size" label="文件大小" width="100">
                <template #default="scope">
                  <span class="size-text">{{ scope.row.size }}</span>
                </template>
              </el-table-column>
              <el-table-column fixed="right" label="操作" width="120">
                <template #default="scope">
                  <el-button
                    link
                    type="primary"
                    @click="viewHistoryResult(scope.row)"
                    class="view-btn"
                  >
                    查看结果
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="historyRecords.length === 0 && !loadingHistory" class="empty-history">
              <el-empty description="暂无历史记录"></el-empty>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    </div>
  </div>
</template>

<script>
import PredictionTable from '../components/PredictionTable.vue'
import ProteinVisualizer from '../components/ProteinVisualizer.vue'
import Navbar from '../components/Navbar.vue' // 添加导入
import axios from 'axios'
import { Upload, Plus, Minus, Refresh, Setting } from '@element-plus/icons-vue'

export default {
  name: 'Home',
  components: {
    PredictionTable,
    ProteinVisualizer,
    Navbar,
    Upload,
    Plus,
    Minus,
    Refresh,
    Setting
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
      headerStyle: {
        background: '#f5f7fa',
        color: '#606266',
        fontWeight: '600'
      },
      // 存储蛋白质序列信息
      proteinSequences: {}
    }
  },

  computed: {
    proteinOptions() {
      if (!this.predictionResults.length) return []

      // 从结果中提取唯一的蛋白质ID
      const proteinIds = [...new Set(this.predictionResults.map(r => r.protein_id))]
      return proteinIds.map(id => ({
        value: id,
        label: id
      }))
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
    async predictSequence() {
      if (!this.sequence) {
        this.$message.warning('请输入蛋白质序列')
        return
      }

      this.predicting = true
      try {
        const response = await axios.post('/api/predict/sequence', {
          sequence: this.sequence
        })
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
      this.isFastaResult = this.isMultiProteinResult(response.results)

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

    isMultiProteinResult(results) {
      if (!results || results.length === 0) return false

      // 检测是否有多个不同的蛋白质ID
      const uniqueIds = new Set(results.map(r => r.protein_id))
      return uniqueIds.size > 1
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

    getProteinLength(proteinId) {
      const sequence = this.getProteinSequence(proteinId)
      return sequence ? sequence.length : 0
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
        const response = await axios.get(`/api/protein/${proteinId}`, {
          params: { filename: this.currentFileName }
        })

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
        const response = await axios.get('/api/history')
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
        const response = await axios.get(`/api/results/${record.filename}`)
        this.predictionResults = response.data
        this.currentFileName = record.filename

        // 判断是否为FASTA结果
        this.isFastaResult = this.isMultiProteinResult(response.data)

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
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Lato:wght@400;700&family=Roboto:wght@400;500;700&family=Fira+Code&family=Nunito:wght@400;600&display=swap');

/* 应用容器 */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.page-content {
  padding-top: 20px;
  flex: 1;
}

/* 基础字体设置 */
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: #2c3e50;
  font-family: "Nunito", "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: linear-gradient(135deg, #f9fcff 0%, #f6f9fc 100%);
  position: relative;
  overflow: hidden;
}

/* 装饰背景元素 */
.home-container::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="%23e1e8f0" stroke-width="0.5"/><circle cx="50" cy="30" r="10" fill="%23e1e8f0" opacity="0.3"/><circle cx="30" cy="60" r="10" fill="%23e1e8f0" opacity="0.3"/><circle cx="70" cy="60" r="10" fill="%23e1e8f0" opacity="0.3"/></svg>');
  background-repeat: no-repeat;
  opacity: 0.3;
  z-index: -1;
}

/* 标题区域 */
.header-section {
  text-align: center;
  margin-bottom: 35px;
  position: relative;
  padding-bottom: 20px;
}

.header-section::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #4b6cb7, #1976d2);
  border-radius: 3px;
}

/* 主标题优化 */
.main-title {
  font-family: "Montserrat", "Microsoft YaHei", sans-serif;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #2c3e50, #4b6cb7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 10px rgba(75, 108, 183, 0.1);
  animation: fadeIn 1s ease-out;
  position: relative;
}

/* 副标题优化 */
.subtitle {
  font-family: "Lato", "Microsoft YaHei", sans-serif;
  font-size: 1.1rem;
  font-weight: 400;
  color: #607d8b;
  margin-bottom: 20px;
  animation: fadeIn 1.2s ease-out;
  letter-spacing: 0.5px;
}

/* 序列信息标签 */
.sequence-info {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  color: #606266;
  margin-top: auto;
}

.protein-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.protein-length {
  background-color: #f0f5ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  color: #5e7ce0;
}

.protein-info {
  margin: 5px 0;
  font-size: 12px;
  color: #909399;
}

/* 蛋白质卡片优化 */
.protein-card {
  padding: 10px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 6px;
  border: 1px solid #e1e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: 90px;
  border-left: 3px solid transparent;
}

.protein-card.active {
  border-left: 3px solid #1976d2;
  background: linear-gradient(to right, #edf5ff, #f5f9ff);
}

.protein-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(50, 50, 93, 0.1);
  border-color: #c0d6e8;
}

/* 蛋白质列表网格布局优化 */
.protein-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

/* 按钮美化 */
.predict-btn {
  background: linear-gradient(135deg, #4b6cb7, #1976d2);
  border: none;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  font-family: "Montserrat", "Microsoft YaHei", sans-serif;
  font-weight: 600;
  letter-spacing: 0.5px;
  padding: 12px 25px;
  box-shadow: 0 4px 6px rgba(75, 108, 183, 0.2);
}

.predict-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 14px rgba(75, 108, 183, 0.3);
  background: linear-gradient(135deg, #5d7ec9, #1e88e5);
}

/* 改进卡片内边距和层次感 */
:deep(.el-card__body) {
  padding: 20px 25px;
}

:deep(.el-card__header) {
  padding: 18px 25px;
  border-bottom: 1px solid #ebeef5;
  background: linear-gradient(to right, rgba(248, 250, 252, 0.8), rgba(255, 255, 255, 0));
}

/* 为不同的卡片添加微妙的颜色差异 */
.mode-card {
  background: linear-gradient(145deg, #ffffff, #f9fcff);
}

.result-card {
  background: linear-gradient(145deg, #fafcff, #f6faff);
}

.history-card {
  background: linear-gradient(145deg, #f9fcff, #f4f8fc);
}

/* DNA双螺旋装饰 */
.mode-card::after {
  content: '';
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 50px;
  height: 50px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23e1e8f0"><path d="M3,4c0,1.1,0.9,2,2,2s2-0.9,2-2s-0.9-2-2-2S3,2.9,3,4z M18,18c0-1.1,0.9-2,2-2s2,0.9,2,2s-0.9,2-2,2S18,19.1,18,18z M7,14c0-1.1,0.9-2,2-2s2,0.9,2,2s-0.9,2-2,2S7,15.1,7,14z M12,8c0-1.1,0.9-2,2-2s2,0.9,2,2s-0.9,2-2,2S12,9.1,12,8z M7.25,4.75L10.75,8.25 M13.25,10.75L16.75,14.25 M4.75,7.25L8.25,10.75 M15.75,13.75L19.25,17.25"/></svg>');
  background-size: contain;
  opacity: 0.08;
  z-index: 0;
}

/* 添加更多科学感装饰 */
.result-card::after {
  content: '';
  position: absolute;
  top: 10px;
  right: 10px;
  width: 60px;
  height: 60px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="%23e1e8f0"><path d="M25,85h50v5H25V85z M35,30V15h30v15l-15,15L35,30z M40,20v7.5l10,10l10-10V20H40z"/></svg>');
  background-size: contain;
  opacity: 0.08;
  z-index: 0;
}

.mode-selection {
  margin-bottom: 25px;
  display: flex;
  justify-content: center;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #1976d2;
  box-shadow: -1px 0 0 0 #1976d2;
  position: relative;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
}

:deep(.el-radio-button__inner) {
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  border: 1px solid #dcdfe6;
}

:deep(.el-radio-group) {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  padding: 3px;
  background: #f5f7fa;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}

.filename-text {
  font-weight: 500;
  color: #2c3e50;
}

.time-text {
  font-family: 'Fira Code', monospace;
  color: #606266;
}

.size-text {
  font-family: 'Fira Code', monospace;
  color: #606266;
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

:deep(.view-btn) {
  font-weight: 600;
}

.upload-section {
  padding: 10px 0;
  margin-bottom: 10px;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  border: 2px dashed #d9e1ec;
  background: linear-gradient(145deg, #ffffff, #f9fcff);
  border-radius: 8px;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #4b6cb7;
  background: linear-gradient(145deg, #f7faff, #edf6ff);
}

.upload-icon {
  font-size: 40px;
  color: #4b6cb7;
  margin-bottom: 10px;
}

.primary-text {
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
  margin-bottom: 5px;
}

.secondary-text {
  font-size: 14px;
  color: #909399;
}

.sequence-input-section {
  margin: 20px 0;
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
  padding: 15px;
  line-height: 1.8;
  letter-spacing: 1px;
}

.result-section {
  margin-top: 35px;
  position: relative;
}

.result-section::before {
  content: '';
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, transparent, #e1e8f0, transparent);
}

.visualizer-section {
  margin: 30px 0;
  padding: 20px;
  background: linear-gradient(145deg, #f7faff, #edf6ff);
  border-radius: 8px;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.03);
}

.empty-history {
  padding: 30px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.no-protein-selected {
  padding: 30px 0;
}

:deep(.el-empty__description) {
  font-size: 15px;
  color: #909399;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}


@media (max-width: 768px) {
  .protein-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}

@media (max-width: 480px) {
  .protein-grid {
    grid-template-columns: 1fr 1fr;
  }

  .header-section {
    margin-bottom: 20px;
  }
}

/* 添加一些微妙的动画效果 */
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(75, 108, 183, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(75, 108, 183, 0); }
  100% { box-shadow: 0 0 0 0 rgba(75, 108, 183, 0); }
}

.predict-btn:focus {
  animation: pulse 1.5s infinite;
}

/* 选择蛋白质时的过渡效果 */
.selected-protein {
  position: relative;
  padding-left: 15px;
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
  transition: all 0.3s ease;
}

.selected-protein::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: linear-gradient(to bottom, #4b6cb7, #1976d2);
  border-radius: 2px;
}
</style>