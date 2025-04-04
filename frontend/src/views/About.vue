<template>
  <div class="app-container">
    <!-- 顶栏 -->
    <Navbar :showBackButton="false" />
    <div class="page-content">
      <div class="about-container">
        <div class="header-section">
          <h1 class="main-title">关于系统</h1>
          <p class="subtitle">蛋白质功能预测系统介绍与说明</p>
        </div>

        <el-card shadow="hover" class="about-card">
          <template #header>
            <div class="card-header">
              <h2>系统简介</h2>
              <span class="version-tag">当前版本: v1.0.0</span>
            </div>
          </template>
          <div class="about-content">
            <p>蛋白质功能预测系统是一个基于深度学习的生物信息学工具，旨在帮助研究人员快速分析蛋白质序列，预测其可能的功能。本系统采用了最新的序列表示学习和图神经网络技术，提供高精度的蛋白质功能预测服务。</p>

            <p>主要功能包括：</p>
            <ul>
              <li>上传FASTA文件批量预测蛋白质功能</li>
              <li>直接输入序列进行单蛋白质功能预测</li>
              <li>基于GO slim分类体系的功能注释</li>
              <li>蛋白质序列可视化展示</li>
              <li>历史预测记录管理</li>
            </ul>
          </div>
        </el-card>

        <el-card shadow="hover" class="about-card">
          <template #header>
            <div class="card-header">
              <h2>技术架构</h2>
            </div>
          </template>
          <div class="tech-stack">
            <div class="tech-item">
              <div class="tech-icon frontend">
                <i class="el-icon-monitor"></i>
              </div>
              <div class="tech-details">
                <h4>前端技术栈</h4>
                <p>Vue.js 3.0 + Element Plus + Axios</p>
                <p>采用现代化的前端框架，提供友好的用户交互界面和响应式设计，确保在不同设备上有良好的使用体验。</p>
              </div>
            </div>

            <div class="tech-item">
              <div class="tech-icon backend">
                <i class="el-icon-cpu"></i>
              </div>
              <div class="tech-details">
                <h4>后端技术栈</h4>
                <p>Python + Flask + PyTorch</p>
                <p>使用轻量级的Flask框架构建API服务，实现前后端分离架构，保证系统的可扩展性和稳定性。</p>
              </div>
            </div>

            <div class="tech-item">
              <div class="tech-icon model">
                <i class="el-icon-connection"></i>
              </div>
              <div class="tech-details">
                <h4>模型构建</h4>
                <p>ESM2 + 图神经网络 (GNN)</p>
                <p>结合最先进的蛋白质语言模型ESM2与图神经网络，捕捉蛋白质序列中的长程依赖关系，提高功能预测的准确性。</p>
              </div>
            </div>
          </div>
        </el-card>

        <el-card shadow="hover" class="about-card">
          <template #header>
            <div class="card-header">
              <h2>团队信息</h2>
            </div>
          </template>
          <div class="team-info">
            <p>本系统由<a href="https://github.com/gaox" target="_blank" class="developer-link">@gaox</a>开发维护。如有任何问题或建议，请通过以下方式联系我们：</p>
            <ul class="contact-list">
              <li><i class="el-icon-message"></i> 邮箱: thisisgaox@qq.com</li>
              <li><i class="el-icon-office-building"></i> 地址: 苏州科技大学石湖校区</li>
              <li><i class="el-icon-document"></i> 文档: <a href="#">用户使用手册</a></li>
            </ul>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue'

export default {
  name: 'About',
  components: {
    Navbar
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Lato:wght@400;700&family=Roboto:wght@400;500;700&family=Nunito:wght@400;600&display=swap');

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

.about-container {
  max-width: 1000px;
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

.about-card {
  margin-bottom: 25px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  position: relative;
}

.about-card::before {
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

.about-card:hover::before {
  opacity: 1;
}

.about-card:hover {
  box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
  transform: translateY(-3px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  position: relative;
  padding-left: 15px;
  font-family: "Montserrat", "Microsoft YaHei", sans-serif;
  font-weight: 600;
  font-size: 1.25rem;
  color: #2c3e50;
  letter-spacing: 0.3px;
  margin: 0;
}

.card-header h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(to bottom, #4b6cb7, #1976d2);
  border-radius: 2px;
}

.version-tag {
  background: linear-gradient(135deg, #e0f7fa, #b2ebf2);
  color: #00838f;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.about-content {
  line-height: 1.7;
  color: #455a64;
}

.about-content p {
  margin-bottom: 15px;
}

.about-content ul {
  padding-left: 20px;
  margin-bottom: 20px;
}

.about-content li {
  margin-bottom: 8px;
  position: relative;
  padding-left: 5px;
}

.tech-stack {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.tech-item {
  display: flex;
  gap: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.tech-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.tech-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 30px;
  color: white;
  flex-shrink: 0;
}

.tech-icon.frontend {
  background: linear-gradient(135deg, #42b883, #347474);
}

.tech-icon.backend {
  background: linear-gradient(135deg, #3776ab, #2b5b84);
}

.tech-icon.model {
  background: linear-gradient(135deg, #ee4c2c, #c62828);
}

.tech-details {
  flex-grow: 1;
}

.tech-details h4 {
  font-family: "Montserrat", "Microsoft YaHei", sans-serif;
  margin-top: 0;
  margin-bottom: 10px;
  color: #2c3e50;
  font-size: 1.1rem;
}

.tech-details p {
  color: #546e7a;
  margin-bottom: 10px;
  line-height: 1.6;
}

.team-info {
  line-height: 1.7;
  color: #455a64;
}

.contact-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
}

.contact-list li {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.contact-list i {
  color: #1976d2;
  font-size: 18px;
}

.contact-list a {
  color: #1976d2;
  text-decoration: none;
  transition: color 0.3s;
}

.contact-list a:hover {
  color: #4b6cb7;
  text-decoration: underline;
}

.developer-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.developer-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .about-container {
    padding: 15px;
  }

  .main-title {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .tech-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 15px;
  }

  .tech-icon {
    margin-bottom: 10px;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 1.8rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .version-tag {
    align-self: flex-start;
  }
}

</style>