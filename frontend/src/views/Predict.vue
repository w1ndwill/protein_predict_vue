<template>
  <div class="predict">
    <h2>蛋白质功能预测</h2>
    <div class="upload-container">
      <input type="file" @change="onFileChange" accept=".fasta">
      <button @click="uploadFile" :disabled="!selectedFile">开始预测</button>
    </div>
    <div v-if="loading" class="loading">预测中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="results" class="results">
      <h3>预测结果</h3>
      <table>
        <thead>
          <tr>
            <th>蛋白质ID</th>
            <th>功能</th>
            <th>置信度</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in results" :key="result.protein_id">
            <td>{{ result.protein_id }}</td>
            <td>{{ result.function }}</td>
            <td>{{ result.confidence.toFixed(3) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFile: null,
      loading: false,
      error: null,
      results: null
    }
  },
  methods: {
    onFileChange(e) {
      this.selectedFile = e.target.files[0]
    },
    async uploadFile() {
      if (!this.selectedFile) return

      const formData = new FormData()
      formData.append('file', this.selectedFile)

      this.loading = true
      this.error = null

      try {
        const response = await fetch('http://localhost:5000/predict', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) throw new Error('预测失败')

        const data = await response.json()
        this.results = data
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>