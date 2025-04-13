<template>
  <div class="register-container">
    <div class="register-card">
      <h2 class="register-title">注册账号</h2>
      <div class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="username"
            class="form-control" 
            placeholder="请输入用户名"
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="email"
            class="form-control" 
            placeholder="请输入邮箱"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password"
            class="form-control" 
            placeholder="请输入密码"
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="confirmPassword"
            class="form-control" 
            placeholder="请再次输入密码"
          />
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button @click="register" class="register-button" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        
        <div class="login-link">
          已有账号？<router-link :to="{ name: 'login' }">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const validateForm = () => {
  if (!username.value) {
    error.value = '请输入用户名'
    return false
  }
  
  if (!email.value) {
    error.value = '请输入邮箱'
    return false
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    error.value = '请输入有效的邮箱地址'
    return false
  }
  
  if (!password.value) {
    error.value = '请输入密码'
    return false
  }
  
  if (password.value.length < 6) {
    error.value = '密码长度不能少于6位'
    return false
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return false
  }
  
  return true
}

const register = async () => {
  error.value = ''
  
  if (!validateForm()) {
    return
  }
  
  loading.value = true
  
  try {
    const result = await authStore.register({
      username: username.value,
      email: email.value,
      password: password.value
    })
    
    if (result.success) {
      router.push({ name: 'dashboard' })
    } else {
      if (typeof result.error === 'object') {
        // 处理API返回的错误对象
        const errorMessages = []
        for (const field in result.error) {
          errorMessages.push(`${field}: ${result.error[field].join(' ')}`)
        }
        error.value = errorMessages.join('\n')
      } else {
        error.value = result.error || '注册失败，请稍后重试'
      }
    }
  } catch (err) {
    error.value = '注册过程发生错误，请稍后重试'
    console.error('Register error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 450px;
  padding: 30px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.register-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.register-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border 0.3s;
}

.form-control:focus {
  border-color: #4285f4;
  outline: none;
}

.register-button {
  padding: 12px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.register-button:hover {
  background-color: #3367d6;
}

.register-button:disabled {
  background-color: #a9a9a9;
  cursor: not-allowed;
}

.error-message {
  color: #d93025;
  margin-bottom: 15px;
  font-size: 14px;
  white-space: pre-line;
}

.login-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
}

.login-link a {
  color: #4285f4;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 