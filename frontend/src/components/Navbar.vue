<template>
  <div class="navbar" :class="{ 'scrolled': isScrolled }">
    <div class="navbar-content">
      <div class="logo-container">
        <img src="../assets/image.png" alt="Logo" class="logo-img" />
        <span class="logo-text">蛋白质功能预测</span>
      </div>

      <div class="nav-links">
        <router-link to="/" class="nav-link" :class="{ 'active': $route.path === '/' }">首页</router-link>
        <router-link to="/history" class="nav-link" :class="{ 'active': $route.path === '/history' }">历史记录</router-link>
        <router-link to="/about" class="nav-link" :class="{ 'active': $route.path === '/about' }">关于</router-link>
      </div>

      <div class="user-actions">
        <template v-if="isLoggedIn">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">{{ userInitials }}</el-avatar>
              <span class="username">{{ currentUser.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="login-btn">登录</router-link>
          <router-link to="/register" class="register-btn">注册</router-link>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { isAuthenticated, getCurrentUser, logout } from '@/services/authService';
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter();
    const isLoggedIn = ref(false);
    const currentUser = ref(null);
    const isScrolled = ref(false);

    const checkAuthStatus = () => {
      isLoggedIn.value = isAuthenticated();
      currentUser.value = getCurrentUser();
    };

    const handleScroll = () => {
      isScrolled.value = window.scrollY > 10;
    };

    onMounted(() => {
      checkAuthStatus();
      window.addEventListener('scroll', handleScroll);
      // Listen for auth changes
      window.addEventListener('auth-change', checkAuthStatus);
    });

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('auth-change', checkAuthStatus);
    });

    const userInitials = computed(() => {
      if (currentUser.value && currentUser.value.username) {
        return currentUser.value.username.substring(0, 1).toUpperCase();
      }
      return '';
    });

    const handleCommand = (command) => {
      if (command === 'logout') {
        logout();
        router.push('/login');
      } else if (command === 'profile') {
        router.push('/profile');
      }
    };

    return {
      isLoggedIn,
      currentUser,
      isScrolled,
      userInitials,
      handleCommand,
    };
  },
};
</script>

<style scoped>
/* Navbar Styling with Animations */
.navbar {
  background-color: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
  padding: 0;
  width: 100%;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: box-shadow 0.3s ease, background-color 0.3s ease;
}

.navbar.scrolled {
  box-shadow: var(--shadow-md);
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  width: 100%;
  padding: 0 24px;
}

/* Logo Animation */
.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-img {
  height: 36px;
  border-radius: 50%;
  transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.logo-container:hover .logo-img {
  transform: rotate(360deg) scale(1.1);
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-heading);
}

/* Nav Links Animation */
.nav-links {
  display: flex;
  gap: 32px;
}

.nav-link {
  color: var(--color-text);
  text-decoration: none;
  font-weight: 500;
  padding: 8px 4px;
  position: relative;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: var(--color-primary);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background-color: var(--color-primary);
  border-radius: 1px;
  transition: width 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

.nav-link.active {
  color: var(--color-heading);
  font-weight: 600;
}

/* User Actions & Buttons Animation */
.user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.user-avatar {
  background-color: var(--color-secondary);
}

.username {
  color: var(--color-heading);
  font-weight: 500;
}

.login-btn, .register-btn {
  text-decoration: none;
  font-weight: 600;
  border-radius: var(--border-radius-medium);
  padding: 8px 16px;
  font-size: 0.9rem;
  transition: all 0.2s ease-in-out;
  border: 1px solid transparent;
}

.login-btn {
  color: var(--color-primary);
  background-color: transparent;
  border-color: var(--color-primary);
}

.login-btn:hover {
  background-color: var(--color-primary);
  color: var(--color-background-soft);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.register-btn {
  background-color: var(--color-primary);
  color: var(--color-background-soft);
}

.register-btn:hover {
  background-color: var(--color-primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Dropdown theming */
:deep(.el-dropdown-menu) {
  background-color: var(--color-background-soft) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--border-radius-medium);
  box-shadow: var(--shadow-lg);
}

:deep(.el-dropdown-item) {
  color: var(--color-text);
}

:deep(.el-dropdown-item:hover) {
  background-color: var(--color-background-mute);
  color: var(--color-heading);
}
</style>
