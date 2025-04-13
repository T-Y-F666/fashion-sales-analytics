import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// API基础URL
const API_URL = 'http://localhost:8000/api'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理token过期
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // 如果是401错误且不是刷新token的请求，尝试刷新token
    if (error.response?.status === 401 && !originalRequest._retry && 
        originalRequest.url !== '/token/refresh/') {
      
      originalRequest._retry = true
      const authStore = useAuthStore()
      
      // 尝试刷新token
      const refreshed = await authStore.refreshAccessToken()
      
      // 如果刷新成功，重试原请求
      if (refreshed) {
        return apiClient(originalRequest)
      }
    }
    
    return Promise.reject(error)
  }
)

// 数据分析API
export const analysisApi = {
  // 各地区销售数据
  getRegionSales() {
    return apiClient.get('/analysis/region-sales/')
  },
  
  // 服装销售类型占比
  getClothingTypeSales() {
    return apiClient.get('/analysis/clothing-type-sales/')
  },
  
  // 服装价格区间销量
  getPriceRangeSales() {
    return apiClient.get('/analysis/price-range-sales/')
  },
  
  // 服装评价分布
  getRatingDistribution() {
    return apiClient.get('/analysis/rating-distribution/')
  }
}

// 预测API
export const forecastApi = {
  // 销量预测
  getSalesForecast() {
    return apiClient.get('/forecast/sales/')
  },
  
  // 价格预测
  getPriceForecast() {
    return apiClient.get('/forecast/price/')
  }
}

export default apiClient 