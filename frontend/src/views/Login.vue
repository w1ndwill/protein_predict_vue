<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <img src="@/assets/image.png" alt="系统Logo" class="auth-logo" />
        <h1 class="auth-title">蛋白质功能预测系统</h1>
        <p class="auth-subtitle">欢迎回来，请登录您的账户</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="auth-form" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名或邮箱"
            size="large"
            @focus="usernameFocus = true"
            @blur="usernameFocus = false"
          >
            <template #prefix>
              <i class="el-icon-user input-icon" :class="{ 'icon-active': usernameFocus }"></i>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="密码"
            show-password
            type="password"
            size="large"
            @focus="passwordFocus = true"
            @blur="passwordFocus = false"
          >
            <template #prefix>
              <i class="el-icon-lock input-icon" :class="{ 'icon-active': passwordFocus }"></i>
            </template>
          </el-input>
        </el-form-item>

        <div class="form-actions">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <a href="javascript:;" class="forgot-link" @click="forgotPassword">忘记密码?</a>
        </div>

        <el-button
          type="primary"
          class="auth-button"
          @click="handleLogin"
          :loading="loading"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登录' }}
        </el-button>

        <div class="auth-footer">
          <span>还没有账号?</span>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { login } from '@/services/authService'
import '@/assets/styles/auth.css'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: '',
        remember: false
      },
      loading: false,
      usernameFocus: false,
      passwordFocus: false,
      rules: {
        username: [
          { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.checkLoginRedirect();
  },
  methods: {
    async handleLogin() {
      this.$refs.loginFormRef.validate(async (valid) => {
        if (!valid) return;

        this.loading = true;
        try {
          const response = await login(this.loginForm);

          this.$message({
            message: '登录成功',
            type: 'success',
            duration: 1500,
            onClose: () => {
              const redirectPath = this.$route.query.redirect || '/';
              this.$router.push(redirectPath);
            }
          });

        } catch (error) {
          this.$message.error(error.response?.data?.message || '登录失败，请检查用户名和密码');
        } finally {
          this.loading = false;
        }
      });
    },
    forgotPassword() {
      this.$message({
        message: '请联系管理员重置密码',
        type: 'info'
      });
    },
    checkLoginRedirect() {
      if (this.$route.query.redirect) {
        this.$message.info('请先登录以继续操作');
      }
    }
  }
}
</script>

<style scoped>
/* All styles have been moved to /src/assets/styles/auth.css */
</style>
