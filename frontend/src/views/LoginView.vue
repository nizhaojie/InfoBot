<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <div class="auth-title">RAG 智能问答</div>

      <!-- Tab 切换登录/注册 -->
      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>

      <!-- 登录表单 -->
      <el-form v-if="activeTab === 'login'" :model="loginForm" :rules="loginRules" ref="loginFormRef" @submit.prevent="doLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
        </el-form-item>
        <el-button type="primary" native-type="submit" style="width:100%" :loading="loading">登录</el-button>
      </el-form>

      <!-- 注册表单 -->
      <el-form v-else :model="regForm" :rules="regRules" ref="regFormRef" @submit.prevent="doRegister">
        <el-form-item prop="username">
          <el-input v-model="regForm.username" placeholder="用户名（3~32位）" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="regForm.email" placeholder="邮箱" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="regForm.password" type="password" placeholder="密码（至少6位）" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="regForm.confirmPassword" type="password" placeholder="确认密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-button type="primary" native-type="submit" style="width:100%" :loading="loading">注册</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { http } from '../api/index'

const router = useRouter()
const auth = useAuthStore()
const chatStore = useChatStore()
const activeTab = ref('login')
const loading = ref(false)
const rememberMe = ref(!!localStorage.getItem('rememberedUser'))

// 登录表单
const loginFormRef = ref()
const loginForm = ref({ username: localStorage.getItem('rememberedUser') ?? '', password: '' })
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 注册表单
const regFormRef = ref()
const regForm = ref({ username: '', email: '', password: '', confirmPassword: '' })
const regRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 32, message: '用户名长度须在 3~32 个字符之间', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_: any, v: string, cb: any) =>
        v === regForm.value.password ? cb() : cb(new Error('两次密码不一致')),
      trigger: 'blur',
    },
  ],
}

async function doLogin() {
  await loginFormRef.value.validate()
  loading.value = true
  try {
    const res = await http.post('/auth/login', loginForm.value)
    if (rememberMe.value) localStorage.setItem('rememberedUser', loginForm.value.username)
    else localStorage.removeItem('rememberedUser')
    auth.setAuth(res.data.access_token, res.data.username)
    chatStore.clearHistory()  // 清空上一个用户的对话记录
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  await regFormRef.value.validate()
  loading.value = true
  try {
    await http.post('/auth/register', {
      username: regForm.value.username,
      email: regForm.value.email,
      password: regForm.value.password,
    })
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.value.username = regForm.value.username
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.auth-card {
  width: 380px;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.auth-title {
  text-align: center;
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 20px;
}
</style>
