<template>
  <div class="app-container">
    <Navbar />
    <div class="page-content">
      <div class="home-container">
        <div class="header-section reveal">
          <ParticlesBackground />
          <div class="header-content">
            <h1 class="main-title">蛋白质功能预测</h1>
            <p class="subtitle">通过顶尖模型分析FASTA文件或原始序列，精准预测蛋白质功能。</p>
          </div>
        </div>

        <el-row :gutter="20">
          <el-col :span="24" class="reveal">
            <el-card class="mode-card">
              <div class="mode-selection">
                <el-radio-group v-model="predictionMode" size="large">
                  <el-radio-button label="fasta">FASTA 文件</el-radio-button>
                  <el-radio-button label="sequence">原始序列</el-radio-button>
                </el-radio-group>
              </div>

              <file-uploader v-if="predictionMode === 'fasta'" @success="handleSuccess" @error="handleError" />
              <sequence-input v-else @submit="predictSequence" />
            </el-card>
          </el-col>
        </el-row>

        <div v-if="predictionResults.length > 0" class="result-section reveal">
          <el-card class="result-card">
            <template #header>
              <div class="section-header">
                <h2>预测结果</h2>
                <span class="current-file" v-if="currentFileName">{{ currentFileName }}</span>
              </div>
            </template>
            <prediction-table :results="predictionResults" />
            <protein-visualizer v-if="sequence" :sequence="sequence" class="visualizer-section" />
          </el-card>
        </div>

        <div class="reveal">
          <history-table @view-result="viewHistoryResult" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import Navbar from '../components/Navbar.vue';
import FileUploader from '../components/Home/FileUploader.vue';
import SequenceInput from '../components/Home/SequenceInput.vue';
import PredictionTable from '../components/PredictionTable.vue';
import ProteinVisualizer from '../components/ProteinVisualizer.vue';
import HistoryTable from '../components/Home/HistoryTable.vue';
import ParticlesBackground from '../components/ParticlesBackground.vue'; // Import the new component
import { predictFromSequence, getHistoryResult } from '@/services/proteinApi';
import '@/assets/styles/home.css';

export default {
  name: 'Home',
  components: {
    Navbar,
    FileUploader,
    SequenceInput,
    PredictionTable,
    ProteinVisualizer,
    HistoryTable,
    ParticlesBackground, // Register the new component
  },
  setup() {
    const predictionMode = ref('fasta');
    const sequence = ref('');
    const predictionResults = ref([]);
    const currentFileName = ref('');

    const handleSuccess = (response) => {
      predictionResults.value = response.results;
      currentFileName.value = response.filename;
      if (response.results.length > 0) {
        sequence.value = response.results[0].sequence;
      }
    };

    const handleError = (error) => {
      console.error('Prediction failed:', error);
    };

    const predictSequence = async (seq) => {
      try {
        const response = await predictFromSequence(seq);
        handleSuccess(response.data);
      } catch (error) {
        handleError(error);
      }
    };

    const viewHistoryResult = async (record) => {
      try {
        const response = await getHistoryResult(record.filename);
        handleSuccess({ results: response.data, filename: record.filename });
      } catch (error) {
        handleError(error);
      }
    };

    onMounted(() => {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });

      document.querySelectorAll('.reveal').forEach(elem => {
        observer.observe(elem);
      });
    });

    return {
      predictionMode,
      sequence,
      predictionResults,
      currentFileName,
      handleSuccess,
      handleError,
      predictSequence,
      viewHistoryResult,
    };
  },
};
</script>

<style scoped>
.header-section {
  position: relative; /* Required for the particle background to be contained */
  padding: 6rem 2rem;
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-large);
  overflow: hidden; /* Ensures the particles don't spill out */
  border: 1px solid var(--color-border);
}

.header-content {
  position: relative; /* Ensures text is on top of particles */
  z-index: 1;
}

.visualizer-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: var(--color-background);
  border-radius: var(--border-radius-medium);
}
</style>
