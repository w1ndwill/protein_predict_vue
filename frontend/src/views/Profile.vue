<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <div class="profile-header">
        <div class="avatar-container">
          <el-avatar :size="80" :src="userAvatar">{{ userInitials }}</el-avatar>
        </div>
        <h1 class="profile-title">个人中心</h1>
        <p class="profile-subtitle">管理您的个人信息和设置</p>
      </div>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <el-form
            :model="userForm"
            :rules="rules"
            ref="userForm"
            label-width="100px"
            class="profile-form">

            <el-form-item label="用户名" prop="username">
              <el-input v-model="userForm.username" disabled></el-input>
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="userForm.email"></el-input>
            </el-form-item>

            <el-form-item label="机构" prop="organization">
              <el-input v-model="userForm.organization"></el-input>
            </el-form-item>

            <el-form-item label="研究领域">
              <el-select v-model="userForm.researchArea" placeholder="选择研究领域" style="width: 100%">
                <el-option label="结构生物学" value="structural_biology"></el-option>
                <el-option label="蛋白质组学" value="proteomics"></el-option>
                <el-option label="生物信息学" value="bioinformatics"></el-option>
                <el-option label="分子生物学" value="molecular_biology"></el-option>
                <el-option label="其他" value="other"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="loading">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="修改密码" name="password">
          <el-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordForm"
            label-width="100px"
            class="profile-form">

            <el-form-item label="当前密码" prop="currentPassword">
              <el-input type="password" v-model="passwordForm.currentPassword" show-password></el-input>
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
              <el-input type="password" v-model="passwordForm.newPassword" show-password></el-input>
              <div class="password-strength">
                <span class="strength-label">密码强度:</span>
                <div class="strength-meter">
                  <div :class="['strength-level', passwordStrengthClass]"></div>
                </div>
                <span class="strength-text" :style="{color: passwordStrengthColor}">{{ passwordStrengthText }}</span>
              </div>
            </el-form-item>

            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input type="password" v-model="passwordForm.confirmPassword" show-password></el-input>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="passwordLoading">更新密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="预测历史" name="history">
          <div class="history-section">
            <el-empty v-if="predictions.length === 0" description="暂无预测历史记录"></el-empty>
            <el-table v-else :data="predictions" style="width: 100%" border>
              <el-table-column prop="timestamp" label="时间" width="180">
                <template #default="scope">
                  <span class="time-text">{{ formatDate(scope.row.timestamp) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="protein_id" label="蛋白质ID" width="180">
                <template #default="scope">
                  <span class="filename-text">{{ scope.row.protein_id }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="function" label="预测功能">
                <template #default="scope">
                  <el-tag type="success">{{ scope.row.function }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="confidence" label="置信度" width="120">
                <template #default="scope">
                  <el-progress :percentage="Math.round(scope.row.confidence * 100)" :format="percentageFormat"></el-progress>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button size="small" type="primary" @click="viewPrediction(scope.row)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-pagination
              v-if="predictions.length > 0"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-size="pageSize"
              layout="total, prev, pager, next"
              :total="totalPredictions"
              class="pagination">
            </el-pagination>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    // 确认密码验证
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    };

    return {
      activeTab: 'info',
      loading: false,
      passwordLoading: false,
      userAvatar: '',
      userForm: {
        username: '',
        email: '',
        organization: '',
        researchArea: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      rules: {
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        organization: [
          { max: 50, message: '机构名称不能超过50个字符', trigger: 'blur' }
        ]
      },
      passwordRules: {
        currentPassword: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 8, message: '密码长度不能少于8个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      predictions: [],
      currentPage: 1,
      pageSize: 10,
      totalPredictions: 0
    };
  },
  computed: {
    userInitials() {
      // 显示用户名首字母作为默认头像
      return this.userForm.username ? this.userForm.username.charAt(0).toUpperCase() : '?';
    },
    passwordStrength() {
      const pwd = this.passwordForm.newPassword;
      if (!pwd) return 0;

      let score = 0;
      // 基本长度分数
      if (pwd.length >= 8) score += 1;
      if (pwd.length >= 12) score += 1;

      // 复杂度分数
      if (/[A-Z]/.test(pwd)) score += 1;
      if (/[a-z]/.test(pwd)) score += 1;
      if (/[0-9]/.test(pwd)) score += 1;
      if (/[^A-Za-z0-9]/.test(pwd)) score += 1;

      return Math.min(score, 4);
    },
    passwordStrengthClass() {
      const strength = this.passwordStrength;
      if (strength <= 1) return 'weak';
      if (strength === 2) return 'medium';
      if (strength === 3) return 'good';
      return 'strong';
    },
    passwordStrengthText() {
      const strength = this.passwordStrength;
      if (strength <= 1) return '弱';
      if (strength === 2) return '中';
      if (strength === 3) return '良好';
      return '强';
    },
    passwordStrengthColor() {
      const strength = this.passwordStrength;
      if (strength <= 1) return '#ff5252';
      if (strength === 2) return '#ffb74d';
      if (strength === 3) return '#4caf50';
      return '#2196f3';
    }
  },
  methods: {
    updateProfile() {
      this.$refs.userForm.validate((valid) => {
        if (valid) {
          this.loading = true;
          // 这里调用后端API更新用户信息
          setTimeout(() => {
            this.loading = false;
            this.$message.success('个人信息更新成功');
          }, 1000);
        }
      });
    },
    changePassword() {
      this.$refs.passwordForm.validate((valid) => {
        if (valid) {
          this.passwordLoading = true;
          // 这里调用后端API更新密码
          setTimeout(() => {
            this.passwordLoading = false;
            this.$message.success('密码修改成功');
            this.passwordForm = {
              currentPassword: '',
              newPassword: '',
              confirmPassword: ''
            };
          }, 1000);
        }
      });
    },
    fetchUserProfile() {
      // 这里调用后端API获取用户信息
      // 模拟API响应
      setTimeout(() => {
        this.userForm = {
          username: 'user123',
          email: 'user@example.com',
          organization: '生物科技研究所',
          researchArea: 'bioinformatics'
        };
      }, 500);
    },
    fetchPredictionHistory() {
      // 这里调用后端API获取预测历史
      // 模拟API响应
      setTimeout(() => {
        this.predictions = [
          {
            timestamp: '2023-11-15T08:30:45',
            protein_id: 'P12345',
            function: '蛋白质结合',
            confidence: 0.89
          },
          {
            timestamp: '2023-10-22T14:15:20',
            protein_id: 'P67890',
            function: 'DNA结合',
            confidence: 0.75
          },
          {
            timestamp: '2023-09-10T10:05:30',
            protein_id: 'Q34567',
            function: '催化活性',
            confidence: 0.92
          }
        ];
        this.totalPredictions = this.predictions.length;
      }, 500);
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },
    percentageFormat(val) {
      return val + '%';
    },
    viewPrediction(prediction) {
      // 跳转到预测详情页面
      this.$message.info(`查看预测: ${prediction.protein_id}`);
    },
    handleCurrentChange(page) {
      this.currentPage = page;
      this.fetchPredictionHistory();
    }
  },
  mounted() {
    this.fetchUserProfile();
    this.fetchPredictionHistory();
  }
};
</script>

<style scoped>
@import "../assets/styles/auth.css";

.profile-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 20px;
  position: relative;
}

.profile-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
}

.profile-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4b6cb7, #1976d2);
}

.profile-header {
  text-align: center;
  padding: 20px 0 30px;
  margin-bottom: 10px;
  position: relative;
}

.avatar-container {
  margin-bottom: 15px;
}

.profile-title {
  font-family: "Montserrat", "Microsoft YaHei", sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2c3e50, #4b6cb7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}

.profile-subtitle {
  font-family: "Lato", "Microsoft YaHei", sans-serif;
  color: #607d8b;
  font-size: 0.95rem;
}

.profile-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.history-section {
  padding: 10px 0;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

/* 从auth.css继承密码强度组件样式 */

/* 适配移动设备 */
@media (max-width: 768px) {
  .profile-container {
    padding: 10px;
  }

  .profile-form {
    padding: 10px;
  }
}
</style>