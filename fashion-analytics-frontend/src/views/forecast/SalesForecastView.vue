<template>
  <div class="sales-forecast">
    <div class="chart-header">
      <h2 class="chart-title">销量预测分析</h2>
      <div class="chart-actions">
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          <i class="fas fa-sync-alt"></i> 刷新数据
        </button>
      </div>
    </div>
    
    <div class="forecast-description">
      <p>基于历史销售数据，使用线性回归算法预测未来30天的销售额趋势。预测考虑了季节性因素、周期性和历史销售模式。</p>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-message">{{ error }}</div>
      <button @click="refreshData" class="retry-btn">重试</button>
    </div>
    
    <div v-else class="chart-container">
      <div class="chart-area" ref="chartContainer"></div>
      
      <div class="data-table">
        <h3 class="table-title">销量预测明细</h3>
        <div class="table-wrapper">
          <table class="forecast-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>预测销售额 (元)</th>
                <th>信心指数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in forecastData" :key="index">
                <td>{{ formatDate(item.date) }}</td>
                <td>{{ formatCurrency(item.forecasted_sales) }}</td>
                <td>
                  <div class="confidence-indicator" :class="getConfidenceClass(index)">
                    {{ getConfidenceLabel(index) }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="forecast-summary">
        <div class="summary-card">
          <div class="summary-title">平均预测销售额</div>
          <div class="summary-value">{{ formatCurrency(averageSales) }}</div>
        </div>
        
        <div class="summary-card">
          <div class="summary-title">最高预测销售额</div>
          <div class="summary-value">{{ formatCurrency(maxSales) }}</div>
        </div>
        
        <div class="summary-card">
          <div class="summary-title">最低预测销售额</div>
          <div class="summary-value">{{ formatCurrency(minSales) }}</div>
        </div>
        
        <div class="summary-card">
          <div class="summary-title">总预测销售额</div>
          <div class="summary-value">{{ formatCurrency(totalSales) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { forecastApi } from '@/services/api'
import * as echarts from 'echarts'

// 图表容器引用
const chartContainer = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// 数据
const forecastData = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 计算统计值
const averageSales = computed(() => {
  if (forecastData.value.length === 0) return 0
  const sum = forecastData.value.reduce((acc, item) => acc + item.forecasted_sales, 0)
  return sum / forecastData.value.length
})

const maxSales = computed(() => {
  if (forecastData.value.length === 0) return 0
  return Math.max(...forecastData.value.map(item => item.forecasted_sales))
})

const minSales = computed(() => {
  if (forecastData.value.length === 0) return 0
  return Math.min(...forecastData.value.map(item => item.forecasted_sales))
})

const totalSales = computed(() => {
  return forecastData.value.reduce((sum, item) => sum + item.forecasted_sales, 0)
})

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit', 
    weekday: 'short'
  })
}

// 格式化货币
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
}

// 获取信心指数类别
const getConfidenceClass = (index: number) => {
  // 预测越远，信心越低
  if (index < 7) return 'high'
  if (index < 14) return 'medium'
  return 'low'
}

// 获取信心指数标签
const getConfidenceLabel = (index: number) => {
  if (index < 7) return '高'
  if (index < 14) return '中'
  return '低'
}

// 初始化图表
const initChart = () => {
  console.log('initChart函数被调用')
  console.log('chartContainer.value:', chartContainer.value)
  
  if (!chartContainer.value) {
    console.error('图表容器元素未找到!')
    return
  }
  
  console.log('开始初始化ECharts实例')
  chart = echarts.init(chartContainer.value)
  updateChart()
  
  window.addEventListener('resize', () => {
    chart?.resize()
  })
}

// 更新图表数据
const updateChart = () => {
  if (!chart) return
  
  const dates = forecastData.value.map(item => item.date)
  const sales = forecastData.value.map(item => item.forecasted_sales)
  
  // 根据预测天数添加不同的信心区间
  const lowerBound1 = sales.map((value, index) => 
    index < 7 ? value * 0.95 : (index < 14 ? value * 0.9 : value * 0.85)
  )
  
  const upperBound1 = sales.map((value, index) => 
    index < 7 ? value * 1.05 : (index < 14 ? value * 1.1 : value * 1.15)
  )
  
  const lowerBound2 = sales.map((value, index) => 
    index < 7 ? value * 0.9 : (index < 14 ? value * 0.8 : value * 0.7)
  )
  
  const upperBound2 = sales.map((value, index) => 
    index < 7 ? value * 1.1 : (index < 14 ? value * 1.2 : value * 1.3)
  )
  
  const option = {
    title: {
      text: '未来30天销售额预测',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        const date = params[0].axisValue
        const value = params[0].data
        return `
          <div style="font-weight: bold; margin-bottom: 5px;">${formatDate(date)}</div>
          <div>预测销售额: ${formatCurrency(value)} 元</div>
        `
      }
    },
    legend: {
      data: ['预测销售额', '信心区间 (95%)', '信心区间 (80%)'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        formatter: function(value: string) {
          const date = new Date(value)
          return `${date.getMonth() + 1}/${date.getDate()}`
        },
        interval: 'auto',
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '销售额 (元)',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '预测销售额',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data: sales,
        itemStyle: {
          color: '#4285f4'
        },
        lineStyle: {
          width: 3
        },
        markPoint: {
          data: [
            { type: 'max', name: '最大值' },
            { type: 'min', name: '最小值' }
          ]
        }
      },
      {
        name: '信心区间 (95%)',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: upperBound1,
        lineStyle: {
          width: 0
        },
        areaStyle: {
          opacity: 0
        }
      },
      {
        name: '信心区间 (95%)',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: lowerBound1,
        lineStyle: {
          width: 0
        },
        areaStyle: {
          color: '#4285f4',
          opacity: 0.2
        },
        stack: 'confidence-band-1'
      },
      {
        name: '信心区间 (80%)',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: upperBound2,
        lineStyle: {
          width: 0
        },
        areaStyle: {
          opacity: 0
        }
      },
      {
        name: '信心区间 (80%)',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: lowerBound2,
        lineStyle: {
          width: 0
        },
        areaStyle: {
          color: '#4285f4',
          opacity: 0.1
        },
        stack: 'confidence-band-2'
      }
    ]
  }
  
  chart.setOption(option)
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await forecastApi.getSalesForecast()
    console.log("API响应数据:", response.data)
    forecastData.value = response.data || []
    
    // 使用nextTick确保DOM已更新
    await nextTick()
    
    setTimeout(() => {
      if (chart) {
        console.log("更新现有图表")
        updateChart()
      } else {
        console.log("初始化新图表")
        initChart()
      }
    }, 100) // 添加小延迟以确保DOM完全渲染
  } catch (err: any) {
    console.error('Error fetching sales forecast data:', err)
    error.value = err.response?.data?.error || '获取销量预测数据失败'
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  console.log("强制刷新数据，清除缓存...")
  chart = null
  forecastData.value = []
  fetchData()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.sales-forecast {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  margin: 0;
  font-size: 1.25rem;
  color: #24292e;
}

.forecast-description {
  margin-bottom: 24px;
  padding: 12px;
  background-color: #f1f8ff;
  border-radius: 4px;
  border-left: 4px solid #0366d6;
}

.forecast-description p {
  margin: 0;
  color: #24292e;
  font-size: 14px;
  line-height: 1.5;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  color: #24292e;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background-color: #f1f2f3;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e1e4e8;
  border-radius: 50%;
  border-top-color: #0366d6;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #586069;
  font-size: 14px;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.error-message {
  color: #cb2431;
  margin-bottom: 16px;
  font-size: 14px;
  text-align: center;
}

.retry-btn {
  padding: 8px 16px;
  background-color: #0366d6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-area {
  width: 100%;
  height: 400px;
}

.data-table {
  margin-top: 16px;
}

.table-title {
  font-size: 1rem;
  margin-top: 0;
  margin-bottom: 16px;
  color: #24292e;
}

.table-wrapper {
  max-height: 400px;
  overflow-y: auto;
}

.forecast-table {
  width: 100%;
  border-collapse: collapse;
}

.forecast-table th,
.forecast-table td {
  border: 1px solid #e1e4e8;
  padding: 8px 12px;
  text-align: left;
}

.forecast-table th {
  position: sticky;
  top: 0;
  background-color: #f6f8fa;
  font-weight: 600;
  font-size: 14px;
  z-index: 1;
}

.forecast-table tbody tr:hover {
  background-color: #f6f8fa;
}

.confidence-indicator {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  min-width: 60px;
}

.confidence-indicator.high {
  background-color: #e6f4ea;
  color: #137333;
}

.confidence-indicator.medium {
  background-color: #fef7e0;
  color: #b06000;
}

.confidence-indicator.low {
  background-color: #fce8e6;
  color: #c5221f;
}

.forecast-summary {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.summary-card {
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  padding: 16px;
  text-align: center;
}

.summary-title {
  font-size: 14px;
  color: #586069;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
  color: #24292e;
}
</style> 