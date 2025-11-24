<template>
  <div class="about-page">
    <Navbar :showBackButton="false" />
    <section class="hero">
      <div class="hero-content reveal">
        <p class="eyebrow">蛋白质功能预测平台</p>
        <h1>探索序列背后的功能洞察</h1>
        <p class="lead">
          结合深度学习与图神经网络的多模态分析引擎，帮助科研团队以更高效率挖掘蛋白质功能潜力。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/')">
            开始预测
          </el-button>
          <el-button plain size="large" @click="$router.push('/history')">
            查看历史
          </el-button>
        </div>
        <ul class="hero-stats">
          <li>
            <span class="stat-value">1,200+</span>
            <span class="stat-label">已分析序列</span>
          </li>
          <li>
            <span class="stat-value">93%</span>
            <span class="stat-label">平均准确率</span>
          </li>
          <li>
            <span class="stat-value">15min</span>
            <span class="stat-label">单批次平均耗时</span>
          </li>
        </ul>
      </div>
      <div class="hero-visual reveal">
        <div class="orb large"></div>
        <div class="orb small"></div>
        <div class="patterns">
          <span v-for="n in 12" :key="n"></span>
        </div>
        <div class="badge-card">
          <p>当前版本</p>
          <strong>v1.0.0</strong>
          <small>模型：ESM2 + GNN</small>
        </div>
      </div>
    </section>

    <section class="panel-grid">
      <el-card shadow="never" class="glass about-card reveal">
        <template #header>
          <div class="card-header">
            <h2>系统简介</h2>
            <span class="pill">深度学习驱动</span>
          </div>
        </template>
        <div class="card-body">
          <p>
            蛋白质功能预测系统以最新序列表示学习与图神经网络技术为核心，支持单序列实时推断与批量FAST A上传分析，覆盖GO slim标准注释体系。
          </p>
          <ul class="feature-list">
            <li>批量/单次预测流程一键切换</li>
            <li>本地缓存与历史追溯</li>
            <li>多视角可视化强化理解</li>
          </ul>
        </div>
      </el-card>

      <el-card shadow="never" class="glass about-card reveal">
        <template #header>
          <div class="card-header">
            <h2>技术架构</h2>
          </div>
        </template>
        <div class="tech-stack">
          <article class="tech-item" v-for="item in techList" :key="item.title">
            <div :class="['tech-icon', item.variant]">
              <i :class="item.icon"></i>
            </div>
            <div class="tech-details">
              <h4>{{ item.title }}</h4>
              <p>{{ item.desc }}</p>
              <p class="extra">{{ item.extra }}</p>
            </div>
          </article>
        </div>
      </el-card>
    </section>

    <section class="timeline-section reveal">
      <header>
        <p class="eyebrow">演进历程</p>
        <h2>持续迭代的能力矩阵</h2>
        <p class="subtitle">从数据预处理、特征抽取到模型推理，全链路不断优化。</p>
      </header>
      <div class="timeline">
        <div class="timeline-item" v-for="item in roadmap" :key="item.phase">
          <div class="timeline-badge">{{ item.phase }}</div>
          <div class="timeline-card">
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <ul>
              <li v-for="point in item.points" :key="point">{{ point }}</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="team-card reveal">
      <el-card shadow="never" class="glass">
        <template #header>
          <div class="card-header">
            <h2>团队信息</h2>
            <span class="pill">联系与支持</span>
          </div>
        </template>
        <div class="team-info">
          <p>
            本系统由
            <a href="https://github.com/w1ndwill?tab=repositories" target="_blank" class="developer-link">@gaox</a>
            持续维护，欢迎反馈与共建。
          </p>
          <ul class="contact-list">
            <li>
              <i class="el-icon-message"></i>
              <div>
                <strong>邮箱</strong>
                <span>thisisgaox@qq.com</span>
              </div>
            </li>
            <li>
              <i class="el-icon-office-building"></i>
              <div>
                <strong>地址</strong>
                <span>苏州科技大学石湖校区</span>
              </div>
            </li>
            <li>
              <i class="el-icon-document"></i>
              <div>
                <strong>文档</strong>
                <a href="#">用户使用手册</a>
              </div>
            </li>
          </ul>
        </div>
      </el-card>
    </section>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import Navbar from '../components/Navbar.vue'

export default {
  name: 'About',
  components: {
    Navbar
  },
  setup() {
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

    const techList = [
      {
        title: '前端技术栈',
        desc: 'Vue 3 + Element Plus + Vite 形成现代化交互体验，配合 Axios 进行数据联动。',
        extra: '支持响应式布局与组件化扩展。',
        icon: 'el-icon-monitor',
        variant: 'frontend'
      },
      {
        title: '后端技术栈',
        desc: 'Flask 提供轻量 API 服务，PyTorch 完成推理，SQLite 负责用户与缓存数据。',
        extra: '具备水平扩展潜力，可接入消息队列或云推理。',
        icon: 'el-icon-cpu',
        variant: 'backend'
      },
      {
        title: '模型构建',
        desc: 'ESM2 编码长程依赖，结合图神经网络做多标签预测，提升功能识别准确度。',
        extra: '支持静态量化与缓存推理结果。',
        icon: 'el-icon-connection',
        variant: 'model'
      }
    ]

    const roadmap = [
      {
        phase: '01',
        title: '数据与预处理',
        desc: '统一 FASTA 导入、清洗与冗余去除，确保训练与预测一致性。',
        points: ['异构数据融合', '自动化质控', '分布统计']
      },
      {
        phase: '02',
        title: '特征与建模',
        desc: 'ESM2 表征与结构提示结合，构建多视角特征图谱。',
        points: ['序列嵌入强化', 'GNN 关系建模', '多标签学习']
      },
      {
        phase: '03',
        title: '预测与可视化',
        desc: '后端推理与缓存策略提升吞吐，前端多模态展示结果细节。',
        points: ['批量推理调度', '历史记录归档', '可视化讲解']
      }
    ]

    return {
      techList,
      roadmap
    }
  }
}
</script>

<style scoped>
/* Using variables from theme.css */
.about-page {
  min-height: 100vh;
  padding: 80px clamp(1rem, 5vw, 80px) 60px;
  background: var(--color-background);
  color: var(--color-text);
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 40px;
  align-items: center;
  margin-bottom: 60px;
}

.hero-content {
  padding: 32px;
}

.eyebrow {
  letter-spacing: 0.3em;
  color: var(--color-primary);
  text-transform: uppercase;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.hero-content h1 {
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  color: var(--color-heading);
  margin-bottom: 16px;
  line-height: 1.2;
}

.lead {
  font-size: 1.1rem;
  color: var(--color-text-mute);
  line-height: 1.8;
  margin-bottom: 32px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 40px;
}

.hero-stats {
  display: flex;
  gap: 32px;
  list-style: none;
  padding: 24px 0;
  margin: 0;
  border-top: 1px solid var(--color-border);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  display: block;
  color: var(--color-secondary);
}

.stat-label {
  color: var(--color-text-mute);
  font-size: 0.9rem;
}

.hero-visual {
  position: relative;
  border-radius: 24px;
  padding: 48px;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  min-height: 400px;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(20px);
  opacity: 0.5;
  animation: float 8s ease-in-out infinite;
}

.orb.large {
  width: 250px;
  height: 250px;
  background: var(--color-primary);
  top: 20px;
  right: -50px;
}

.orb.small {
  width: 180px;
  height: 180px;
  background: var(--color-secondary);
  bottom: 40px;
  left: -40px;
  animation-delay: 2s;
}

.badge-card {
  position: relative;
  margin-top: 40px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 20px;
  color: var(--color-heading);
  width: fit-content;
}

/* Other sections */
.panel-grid, .timeline-section, .team-card {
  max-width: 1000px;
  margin: 0 auto 60px;
}

.glass {
  border-radius: 20px;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  font-size: 1.5rem;
  color: var(--color-heading);
}

.pill {
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--color-background);
  color: var(--color-primary);
  font-size: 0.85rem;
  font-weight: 500;
}

.card-body {
  line-height: 1.8;
  color: var(--color-text);
}

.tech-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tech-item {
  display: flex;
  gap: 16px;
  padding: 18px;
  border-radius: 16px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.tech-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.tech-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 24px;
  color: #fff;
}
.tech-icon.frontend { background: var(--color-primary); }
.tech-icon.backend { background: var(--color-secondary); }
.tech-icon.model { background: #3182CE; } /* Blue */

.timeline-section header {
  text-align: center;
  margin-bottom: 40px;
}

.timeline-section .subtitle {
  max-width: 500px;
  margin: 0 auto;
  color: var(--color-text-mute);
}

.timeline {
  display: grid;
  gap: 24px;
  margin-top: 24px;
}

.timeline-item {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 24px;
}

.timeline-badge {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-background-soft);
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  display: grid;
  place-items: center;
  font-size: 1.8rem;
  font-weight: 700;
}

.timeline-card {
  padding: 24px;
  border-radius: 20px;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
}

.team-info ul {
  list-style: none;
  padding: 0;
  margin: 24px 0 0;
  display: grid;
  gap: 16px;
}

/* Reveal Animation */
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

@keyframes float {
  0% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
  100% { transform: translateY(0); }
}
</style>
