<template>
  <div class="navbar">
    <div class="navbar-content">
      <div class="logo-container"
           @mouseenter="showPreview = true"
           @mouseleave="showPreview = false">
        <img src="../assets/image.png" alt="Logo" class="logo-img" />
        <span class="logo-text">蛋白质功能预测</span>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-link" :class="{ 'active': currentPath === '/' }">首页</router-link>
        <router-link to="/history" class="nav-link" :class="{ 'active': currentPath === '/history' }">历史记录</router-link>
        <router-link to="/about" class="nav-link" :class="{ 'active': currentPath === '/about' }">关于系统</router-link>
      </div>
      <div class="user-actions">
        <el-tooltip content="系统设置" placement="bottom">
          <el-button circle text>
            <el-icon><Setting /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 将预览弹窗移到DOM最外层 -->
    <teleport to="body">
      <div class="logo-preview-container" v-if="showPreview">
        <div class="logo-preview" :style="previewStyle">
          <img src="../assets/image.png" alt="Logo预览" />
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
import { Setting } from '@element-plus/icons-vue'
import { ref, computed, onMounted } from 'vue'

export default {
  components: {
    Setting
  },
  props: {
    showBackButton: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      showPreview: false
    }
  },
  computed: {
    currentPath() {
      return this.$route.path;
    },
    previewStyle() {
      // 动态计算预览窗口位置
      const logoEl = document.querySelector('.logo-container');
      if (logoEl) {
        const rect = logoEl.getBoundingClientRect();
        return {
          position: 'fixed',
          top: `${rect.bottom + 10}px`,
          left: `${rect.left}px`
        };
      }
      return {};
    }
  },
}
</script>

<style scoped>
/* 复制Home.vue中的导航栏样式 */
.navbar {
  background: linear-gradient(90deg, #2c3e50, #4b6cb7);
  padding: 0;
  width: 100%;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  position: relative;
}

.logo-preview-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  pointer-events: none;
}

.logo-container {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  margin-right: 0;
  margin-left: 0;
  transition: all 0.3s ease;
  position: relative;
}

.logo-container:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.logo-img {
  height: 32px;
  margin-right: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.logo-container:hover .logo-img {
  transform: scale(1.1);
}

/* 预览弹窗样式 */
.logo-preview {
  position: absolute;
  background: transparent; /* 移除白色背景 */
  border-radius: 12px;
  padding: 0; /* 移除内边距 */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); /* 更强的阴影效果 */
  pointer-events: auto;
  animation: fadeIn 0.25s ease;
  overflow: hidden; /* 确保内容不溢出圆角边界 */
}

.logo-preview img {
  max-width: 200px;
  max-height: 180px; /* 限制最大高度 */
  border-radius: 8px;
  display: block; /* 移除图片底部间隙 */
  object-fit: cover; /* 保持图片比例 */
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.15)); /* 给图片添加阴影 */
  transform-origin: center;
  animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); /* 弹性动画 */
}

@keyframes scaleIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.logo-text {
  font-family: "Montserrat", "Microsoft YaHei", sans-serif;
  font-weight: 600;
  font-size: 1.2rem;
  letter-spacing: 0.3px;
  background: linear-gradient(90deg, #ffffff, #e1e8f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.nav-links {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 25px;
}

.nav-link {
  color: #e1e8f0;
  text-decoration: none;
  font-weight: 500;
  padding: 6px 0;
  position: relative;
  transition: color 0.3s;
}

.nav-link:hover, .nav-link.active {
  color: white;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: white;
  transition: width 0.3s;
}

.nav-link:hover::after, .nav-link.active::after {
  width: 100%;
}

.user-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .nav-links {
    gap: 15px;
  }

  .logo-text {
    font-size: 1rem;
  }
}
</style>