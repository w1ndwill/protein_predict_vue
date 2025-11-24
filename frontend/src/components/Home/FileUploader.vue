<template>
  <div class="upload-section">
    <el-upload
      class="upload-demo"
      drag
      action="/api/predict"
      accept=".fasta"
      name="file"
      :on-success="handleSuccess"
      :on-error="handleError"
      :show-file-list="true"
      :loading="loading"
    >
      <el-icon class="upload-icon"><upload /></el-icon>
      <div class="upload-text">
        <p class="primary-text">拖拽FASTA文件到此处</p>
        <p class="secondary-text">或点击上传</p>
      </div>
    </el-upload>
  </div>
</template>

<script>
import { Upload } from '@element-plus/icons-vue'

export default {
  name: 'FileUploader',
  components: { Upload },
  props: {
    loading: Boolean
  },
  methods: {
    handleSuccess(response) {
      this.$emit('success', response)
    },
    handleError(error) {
      this.$emit('error', error)
    }
  }
}
</script>