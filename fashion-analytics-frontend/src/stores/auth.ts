import { defineStore } from 'pinia'
import axios from 'axios'

// API基础URL
const API_URL = 'http://localhost:8000/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    refreshToken: localStorage.getItem('refreshToken')
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  
  actions: {
    async login(username: string, password: string) {
      try {
        const response = await axios.post(`${API_URL}/auth/login/`, {
          username,
          password
        })
        
        const { user, access, refresh } = response.data
        
        this.user = user
        this.token = access
        this.refreshToken = refresh
        
        localStorage.setItem('token', access)
        localStorage.setItem('refreshToken', refresh)
        
        // 设置axios默认头部
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        
        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.error || '登录失败'
        }
      }
    },
    
    async register(userData: { username: string; email: string; password: string }) {
      try {
        const response = await axios.post(`${API_URL}/auth/register/`, userData)
        
        const { user, access, refresh } = response.data
        
        this.user = user
        this.token = access
        this.refreshToken = refresh
        
        localStorage.setItem('token', access)
        localStorage.setItem('refreshToken', refresh)
        
        // 设置axios默认头部
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        
        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data || '注册失败'
        }
      }
    },
    
    async refreshAccessToken() {
      if (!this.refreshToken) return false
      
      try {
        const response = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: this.refreshToken
        })
        
        const { access } = response.data
        this.token = access
        localStorage.setItem('token', access)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        
        return true
      } catch (error) {
        this.logout()
        return false
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      delete axios.defaults.headers.common['Authorization']
    }
  }
}) 