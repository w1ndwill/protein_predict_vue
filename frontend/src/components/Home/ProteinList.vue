<template>
  <div class="protein-list-section">
    <h3>蛋白质列表</h3>
    <div class="protein-grid">
      <el-card
        v-for="protein in proteins"
        :key="protein.value"
        class="protein-card"
        :class="{'active': selectedId === protein.value}"
        shadow="hover"
        @click="selectProtein(protein.value)"
      >
        <div class="protein-name">{{ protein.label }}</div>
        <div class="protein-info">
          <span class="protein-length">序列长度: {{ getLength(protein.value) }}</span>
        </div>
        <div class="protein-actions">
          <el-button size="small" type="primary" plain>查看详情</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProteinList',
  props: {
    proteins: {
      type: Array,
      default: () => []
    },
    selectedId: String,
    sequences: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    selectProtein(id) {
      this.$emit('select', id)
    },
    getLength(id) {
      const sequence = this.sequences[id] || ''
      return sequence.length
    }
  }
}
</script>

<style scoped>
.protein-list-section {
  margin-bottom: 20px;
}

.protein-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.protein-card {
  cursor: pointer;
  transition: all 0.3s;
}

.protein-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.protein-card.active {
  border: 2px solid #409eff;
}

.protein-name {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 8px;
  color: #303133;
}

.protein-info {
  color: #606266;
  font-size: 13px;
  margin-bottom: 10px;
}

.protein-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 5px;
}
</style>