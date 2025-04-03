<template>
  <div class="app-container">
    <!-- 顶栏 -->
    <Navbar :showBackButton="false" />
    <div class="page-content">
      <div class="history-page">
        <div class="header-section">
          <h1 class="main-title">历史预测记录</h1>
          <p class="subtitle">查看和管理之前的蛋白质功能预测记录</p>
        </div>

        <el-card shadow="hover" class="history-card">
          <template #header>
            <div class="section-header">
              <h2>历史记录</h2>
              <el-button size="small" type="primary" plain @click="loadHistory" :icon="Refresh">刷新</el-button>
            </div>
          </template>
          <el-table
            :data="historyRecords"
            style="width: 100%"
            :header-cell-style="headerStyle"
            v-loading="loading"
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
            <el-table-column fixed="right" label="操作" width="160">
              <template #default="scope">
                <el-button
                  link
                  type="primary"
                  @click="viewHistoryResult(scope.row)"
                >
                  查看结果
                </el-button>
                <el-button
                  link
                  type="danger"
                  @click="confirmDelete(scope.row)"
                  :loading="scope.row.deleting"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="historyRecords.length === 0 && !loading" class="empty-history">
            <el-empty description="暂无历史记录"></el-empty>
          </div>
        </el-card>

        <!-- 结果显示区域 -->
        <el-card v-if="predictionResults.length > 0" shadow="hover" class="result-card">
          <template #header>
            <div class="section-header">
              <h2>预测结果详情</h2>
              <span class="current-file">{{ currentFileName }}</span>
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
      </div>
    </div>
  </div>
</template>

<script>
import PredictionTable from '../components/PredictionTable.vue'
import ProteinVisualizer from '../components/ProteinVisualizer.vue'
import Navbar from '../components/Navbar.vue'
import axios from 'axios'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

export default {
  name: 'History',
  components: {
    PredictionTable,
    ProteinVisualizer,
    Navbar,
    Refresh
  },

  data() {
    return {
      loading: false,
      historyRecords: [],
      predictionResults: [],
      currentFileName: '',
      selectedProteinId: '',
      isFastaResult: false,
      sequence: '',
      proteinSequences: {},
      headerStyle: {
        background: '#f5f7fa',
        color: '#606266',
        fontWeight: '600'
      }
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
    this.loadHistory()
  },

  methods: {
    async loadHistory() {
      this.loading = true
      try {
        const response = await axios.get('/api/history')
        this.historyRecords = response.data
      } catch (error) {
        this.$message.error('加载历史记录失败：' + error.message)
        this.historyRecords = []
      } finally {
        this.loading = false
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
          this.selectedProteinId = response.data[0]?.protein_id || ''
        }
      } catch (error) {
        this.$message.error('加载历史结果失败：' + error.message)
      }
    },

    isMultiProteinResult(results) {
      if (!results || results.length === 0) return false
      const uniqueIds = new Set(results.map(r => r.protein_id))
      return uniqueIds.size > 1
    },

    storeProteinSequences(results) {
      results.forEach(result => {
        if (result.protein_id && result.sequence) {
          this.proteinSequences[result.protein_id] = result.sequence
        }
      })
    },

    getProteinSequence(proteinId) {
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

      // 从后端获取
      try {
        const response = await axios.get(`/api/protein/${proteinId}`, {
          params: { filename: this.currentFileName }
        })

        if (response.data.sequence) {
          this.sequence = response.data.sequence
          this.proteinSequences[proteinId] = response.data.sequence
        }
      } catch (error) {
        this.$message.error('获取蛋白质序列失败：' + error.message)
      }
    },

    async confirmDelete(record) {
      try {
        // 显示确认对话框
        await ElMessageBox.confirm(
          `确定要删除记录 ${record.filename} 吗？`,
          '删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        );

        // 设置正在删除状态
        record.deleting = true;

        // 调用删除 API
        const response = await axios.delete(`/api/results/${record.filename}`);

        // 显示成功消息
        ElMessage.success('记录已成功删除');

        // 重新加载历史记录列表
        this.loadHistoryRecords();
      } catch (error) {
        // 处理取消情况
        if (error === 'cancel') {
          ElMessage.info('已取消删除');
        } else {
          // 处理API错误
          ElMessage.error(`删除失败：${error.response?.data?.error || error.message}`);
        }
      } finally {
        // 无论如何都清除删除状态
        record.deleting = false;
      }
    },

    async loadHistoryRecords() {
      this.loading = true;
      try {
        const response = await axios.get('/api/history');
        // 给每条记录添加 deleting 状态字段
        this.historyRecords = response.data.map(record => ({
          ...record,
          deleting: false
        }));
      } catch (error) {
        ElMessage.error('加载历史记录失败：' + error.message);
        this.historyRecords = [];
      } finally {
        this.loading = false;
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

.history-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: #2c3e50;
  font-family: "Nunito", "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: linear-gradient(135deg, #f9fcff 0%, #f6f9fc 100%);
  position: relative;
  overflow: hidden;
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

.history-card, .result-card {
  margin-bottom: 25px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  position: relative;
}

.history-card::before, .result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4b6cb7, #1976d2);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.history-card:hover::before, .result-card:hover::before {
  opacity: 1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  position: relative;
  font-family: "Montserrat", "Microsoft YaHei", sans-serif;
  font-weight: 600;
  font-size: 1.25rem;
  color: #2c3e50;
  letter-spacing: 0.3px;
  margin: 0;
}

.current-file {
  font-size: 14px;
  color: #909399;
}

.protein-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
  margin: 15px 0;
}

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
}

.protein-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(50, 50, 93, 0.1);
  border-color: #c0d6e8;
}

.protein-card.active {
  background: linear-gradient(135deg, #ecf5ff 0%, #e3effd 100%);
  border-color: #4b6cb7;
  box-shadow: 0 3px 10px rgba(75, 108, 183, 0.15);
}

.protein-card.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(to bottom, #4b6cb7, #1976d2);
}

.protein-name {
  font-weight: bold;
  margin-bottom: 8px;
  font-family: "Roboto", "Microsoft YaHei", sans-serif;
}

.protein-info {
  font-size: 12px;
  color: #606266;
}

.protein-actions {
  margin-top: 10px;
}

.selected-protein {
  margin: 10px 0;
  padding: 8px 12px;
  background-color: #f2f6fc;
  border-radius: 4px;
  font-size: 14px;
  border-left: 3px solid #409eff;
}

.visualizer-section {
  margin-top: 20px;
  margin-bottom: 10px;
}

.sequence-info {
  margin-top: 10px;
}

.empty-history {
  padding: 30px 0;
}

.no-protein-selected {
  padding: 20px 0;
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
</style>