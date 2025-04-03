<template>
  <div class="sequence-input-section">
    <el-input
      v-model="value"
      type="textarea"
      :rows="6"
      placeholder="请输入蛋白质序列..."
      :maxlength="1000"
      show-word-limit
      @input="handleInput"
    />

    <div class="button-container">
      <el-button
        type="primary"
        :loading="loading"
        @click="handleSubmit"
        class="predict-btn"
      >
        预测功能
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SequenceInput',
  props: {
    loading: Boolean
  },
  data() {
    return {
      value: ''
    }
  },
  methods: {
    handleInput(val) {
      this.$emit('update:sequence', val)
    },
    handleSubmit() {
      this.$emit('submit', this.value)
    }
  }
}
</script>