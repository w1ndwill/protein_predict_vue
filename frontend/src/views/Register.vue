<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <img src="@/assets/image.png" alt="系统Logo" class="auth-logo rounded-logo" @mouseover="logoHover = true" @mouseleave="logoHover = false" :class="{ 'logo-hover': logoHover }" />
        <h1 class="auth-title">蛋白质功能预测系统</h1>
        <p class="auth-subtitle">创建您的账户，开始预测之旅</p>
      </div>

      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" class="auth-form" @keyup.enter="handleRegister">
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="用户名"
            size="large"
            @focus="usernameFocus = true"
            @blur="usernameFocus = false"
          >
            <template #prefix>
              <i class="el-icon-user input-icon" :class="{ 'icon-active': usernameFocus }"></i>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="邮箱"
            size="large"
            @focus="emailFocus = true"
            @blur="emailFocus = false"
          >
            <template #prefix>
              <i class="el-icon-message input-icon" :class="{ 'icon-active': emailFocus }"></i>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            placeholder="密码"
            show-password
            type="password"
            size="large"
            @focus="passwordFocus = true"
            @blur="passwordFocus = false"
            @input="checkPasswordStrength"
          >
            <template #prefix>
              <i class="el-icon-lock input-icon" :class="{ 'icon-active': passwordFocus }"></i>
            </template>
          </el-input>
        </el-form-item>

        <div class="password-strength" v-if="registerForm.password">
          <span class="strength-label">密码强度:</span>
          <div class="strength-meter">
            <div :class="['strength-level', passwordStrength.level]"></div>
          </div>
          <span class="strength-text" :style="{ color: passwordStrength.color }">
            {{ passwordStrength.text }}
          </span>
        </div>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="确认密码"
            show-password
            type="password"
            size="large"
            @focus="confirmPasswordFocus = true"
            @blur="confirmPasswordFocus = false"
          >
            <template #prefix>
              <i class="el-icon-key input-icon" :class="{ 'icon-active': confirmPasswordFocus }"></i>
            </template>
          </el-input>
        </el-form-item>

        <div class="form-actions">
          <el-checkbox v-model="registerForm.agreement">我已阅读并同意<a href="javascript:;" @click="showTerms">服务条款</a></el-checkbox>
        </div>

        <el-button
          type="primary"
          class="auth-button"
          @click="handleRegister"
          :loading="loading"
          :disabled="loading || !registerForm.agreement"
        >
          {{ loading ? '注册中...' : '注册' }}
        </el-button>

        <div class="auth-footer">
          <span>已有账号?</span>
          <router-link to="/login" class="login-link">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { register } from '@/services/authService'
import '@/assets/styles/auth.css'

export default {
  name: 'Register',
  data() {
    // 自定义验证器：确认密码
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    };

    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        agreement: false
      },
      loading: false,
      usernameFocus: false,
      emailFocus: false,
      passwordFocus: false,
      confirmPasswordFocus: false,
      logoHover: false,
      passwordStrength: {
        level: 'weak',
        text: '弱',
        color: '#ff5252'
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.animateLogo();
  },
  methods: {
    animateLogo() {
      const logo = document.querySelector('.auth-logo');
      if (logo) {
        setTimeout(() => {
          logo.classList.add('animated');
        }, 300);
      }
    },
    checkPasswordStrength() {
      const password = this.registerForm.password;

      if (!password) {
        this.passwordStrength = { level: 'weak', text: '弱', color: '#ff5252' };
        return;
      }

      // 密码强度评分系统
      let score = 0;

      // 长度检查
      if (password.length >= 8) score += 1;
      if (password.length >= 10) score += 1;

      // 包含大写字母
      if (/[A-Z]/.test(password)) score += 1;

      // 包含小写字母
      if (/[a-z]/.test(password)) score += 1;

      // 包含数字
      if (/[0-9]/.test(password)) score += 1;

      // 包含特殊字符
      if (/[^A-Za-z0-9]/.test(password)) score += 1;

      // 根据得分设置强度
      if (score <= 2) {
        this.passwordStrength = { level: 'weak', text: '弱', color: '#ff5252' };
      } else if (score <= 4) {
        this.passwordStrength = { level: 'medium', text: '中', color: '#ffb74d' };
      } else if (score <= 5) {
        this.passwordStrength = { level: 'good', text: '良好', color: '#4caf50' };
      } else {
        this.passwordStrength = { level: 'strong', text: '强', color: '#2196f3' };
      }
    },
    async handleRegister() {
      this.$refs.registerFormRef.validate(async (valid) => {
        if (!valid) return;

        if (!this.registerForm.agreement) {
          this.$message.warning('请阅读并同意服务条款');
          return;
        }

        this.loading = true;
        try {
          const response = await register({
            username: this.registerForm.username,
            email: this.registerForm.email,
            password: this.registerForm.password
          });

          this.$message({
            message: '注册成功，请登录',
            type: 'success',
            duration: 1500,
            onClose: () => {
              this.$router.push('/login');
            }
          });

        } catch (error) {
          const errorMsg = error.response?.data?.message || '注册失败，请稍后再试';
          this.$message.error(errorMsg);
        } finally {
          this.loading = false;
        }
      });
    },
    showTerms() {
      this.$message({
        message: '服务条款内容：使用本系统进行蛋白质功能预测，数据仅用于科研目的。',
        type: 'info',
        duration: 5000
      });
    }
  }
}
</script>

<style scoped>
.icon-active {
  color: #1976d2 !important;
  transform: scale(1.1);
}

.input-icon {
  transition: all 0.3s ease;
}

.logo-hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.rounded-logo {
  border-radius: 12px !important; /* 添加圆角 */
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.auth-logo.animated {
  animation: bounceIn 0.7s cubic-bezier(0.215, 0.61, 0.355, 1);
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale3d(0.3, 0.3, 0.3);
  }
  20% {
    transform: scale3d(1.1, 1.1, 1.1);
  }
  40% {
    transform: scale3d(0.9, 0.9, 0.9);
  }
  60% {
    opacity: 1;
    transform: scale3d(1.03, 1.03, 1.03);
  }
  80% {
    transform: scale3d(0.97, 0.97, 0.97);
  }
  to {
    opacity: 1;
    transform: scale3d(1, 1, 1);
  }
}
</style>