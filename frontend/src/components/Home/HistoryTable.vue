<template>
  <el-card shadow="hover" class="history-card">
    <template #header>
      <div class="section-header">
        <h2>历史预测记录</h2>
        <el-button size="small" type="primary" plain @click="$emit('refresh')">刷新</el-button>
      </div>
    </template>

    <el-table
      :data="records"
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
      <el-table-column fixed="right" label="操作" width="120">
        <template #default="scope">
          <el-button
            link
            type="primary"
            @click="$emit('view-result', scope.row)"
            class="view-btn"
          >
            查看结果
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="records.length === 0 && !loading" class="empty-history">
      <el-empty description="暂无历史记录"></el-empty>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'HistoryTable',
  props: {
    records: {
      type: Array,
      default: () => []
    },
    loading: Boolean
  },
  data() {
    return {
      headerStyle: {
        background: '#f5f7fa',
        color: '#606266',
        fontWeight: '600'
      }
    }
  }
}
</script>