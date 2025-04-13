<template>
  <div class="price-forecast">
    <div class="chart-header">
      <h2 class="chart-title">服装价格预测分析</h2>
      <div class="chart-actions">
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          <i class="fas fa-sync-alt"></i> 刷新数据
        </button>
      </div>
    </div>

    <div class="forecast-description">
      <p>基于历史销售数据、销量和售价关系，预测各类服装的最优定价策略。通过分析销量与价格的关系，为不同类型的服装推荐最佳售价。</p>
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

      <div class="price-recommendations">
        <h3 class="section-title">价格预测明细</h3>

        <div class="recommendations-grid">
          <div
            v-for="item in forecastData"
            :key="item.clothing_type"
            class="recommendation-card"
          >
            <div class="card-header">
              <div class="clothing-type">{{ item.clothing_type }}</div>
              <div :class="getPriceChangeClass(item)">
                {{ getPriceChangeText(item) }}
              </div>
            </div>

            <div class="price-detail">
              <div class="recommended-price">
                <div class="price-label">预测最优价格</div>
                <div class="price-value">¥ {{ formatCurrency(item.forecasted_price) }}</div>
              </div>

              <div class="price-comparison">
                <div class="current-avg-price">
                  <div class="comparison-label">当前平均价格</div>
                  <div class="comparison-value">
                    ¥ {{ formatCurrency(getCurrentPrice(item)) }}
                  </div>
                </div>

                <div class="price-change">
                  <div class="comparison-label">价格调整</div>
                  <div class="comparison-value" :class="getPriceChangeClass(item)">
                    {{ formatPriceChange(item) }}
                  </div>
                </div>
              </div>
            </div>

            <div class="recommendation-reason">
              {{ getRecommendationReason(item) }}
            </div>
          </div>
        </div>
      </div>

      <div class="price-analysis">
        <h3 class="section-title">价格调整分析</h3>

        <div class="analysis-summary">
          <div class="summary-item">
            <div class="summary-label">建议提高价格的服装类型</div>
            <div class="summary-value increase">{{ increasePriceCount }} 种</div>
          </div>

          <div class="summary-item">
            <div class="summary-label">建议保持价格的服装类型</div>
            <div class="summary-value neutral">{{ maintainPriceCount }} 种</div>
          </div>

          <div class="summary-item">
            <div class="summary-label">建议降低价格的服装类型</div>
            <div class="summary-value decrease">{{ decreasePriceCount }} 种</div>
          </div>

          <div class="summary-item">
            <div class="summary-label">平均调整幅度</div>
            <div class="summary-value">{{ averageAdjustmentPercentage }}%</div>
          </div>
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

// 模拟当前价格数据（实际中应从服务器获取）
const getCurrentPrice = (item: any) => {
  // 预测价格基础上加减一点随机值，模拟当前价格
  const randomFactor = 0.85 + Math.random() * 0.3 // 0.85 到 1.15 之间
  return item.forecasted_price * randomFactor;
}

// 价格变化计算
const getPriceChange = (item: any) => {
  const currentPrice = getCurrentPrice(item)
  return item.forecasted_price - currentPrice
}

const getPriceChangePercentage = (item: any) => {
  const currentPrice = getCurrentPrice(item)
  return ((item.forecasted_price - currentPrice) / currentPrice) * 100
}

// 格式化价格变化
const formatPriceChange = (item: any) => {
  const change = getPriceChange(item)
  const percentage = getPriceChangePercentage(item)

  const sign = change > 0 ? '+' : ''
  return `${sign}${formatCurrency(change)} (${sign}${percentage.toFixed(2)}%)`
}

// 获取价格变化的CSS类
const getPriceChangeClass = (item: any) => {
  const change = getPriceChange(item)
  if (Math.abs(change) < 1) return 'neutral'
  return change > 0 ? 'increase' : 'decrease'
}

// 获取价格变化文本
const getPriceChangeText = (item: any) => {
  const change = getPriceChange(item)
  if (Math.abs(change) < 1) return '价格保持'
  return change > 0 ? '建议提高价格' : '建议降低价格'
}

// 获取推荐原因
const getRecommendationReason = (item: any) => {
  const change = getPriceChange(item)

  if (Math.abs(change) < 1) {
    return '当前价格合理，符合市场需求，建议保持。'
  } else if (change > 0) {
    return '销量良好，需求强劲，提高价格可获取更高利润。'
  } else {
    return '当前价格偏高影响销量，适当降低价格可提升销量。'
  }
}

// 统计数据
const increasePriceCount = computed(() => {
  return forecastData.value.filter(item => getPriceChange(item) > 1).length
})

const decreasePriceCount = computed(() => {
  return forecastData.value.filter(item => getPriceChange(item) < -1).length
})

const maintainPriceCount = computed(() => {
  return forecastData.value.filter(item => Math.abs(getPriceChange(item)) <= 1).length
})

const averageAdjustmentPercentage = computed(() => {
  if (forecastData.value.length === 0) return '0.00'

  const sum = forecastData.value.reduce((acc, item) => {
    return acc + Math.abs(getPriceChangePercentage(item))
  }, 0)

  return (sum / forecastData.value.length).toFixed(2)
})

// 格式化货币
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
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

  // 准备数据
  const types = forecastData.value.map(item => item.clothing_type)
  const currentPrices = forecastData.value.map(item => getCurrentPrice(item))
  const forecastedPrices = forecastData.value.map(item => item.forecasted_price)

  const option = {
    title: {
      text: '服装类型价格对比分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        const typeIndex = params[0].dataIndex
        const item = forecastData.value[typeIndex]
        const currentPrice = currentPrices[typeIndex]
        const forecastedPrice = forecastedPrices[typeIndex]
        const change = forecastedPrice - currentPrice
        const changePercentage = (change / currentPrice) * 100

        const sign = change > 0 ? '+' : ''

        return `
          <div style="font-weight: bold; margin-bottom: 5px;">${item.clothing_type}</div>
          <div>当前价格: ¥ ${formatCurrency(currentPrice)}</div>
          <div>预测价格: ¥ ${formatCurrency(forecastedPrice)}</div>
          <div>价格变化: ${sign}${formatCurrency(change)} (${sign}${changePercentage.toFixed(2)}%)</div>
        `
      }
    },
    legend: {
      data: ['当前价格', '预测价格'],
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
      data: types,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '价格 (元)',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '当前价格',
        type: 'bar',
        data: currentPrices,
        itemStyle: {
          color: '#5c7cfa'
        }
      },
      {
        name: '预测价格',
        type: 'bar',
        data: forecastedPrices,
        itemStyle: {
          color: function(params: any) {
            const index = params.dataIndex
            const change = forecastedPrices[index] - currentPrices[index]

            if (Math.abs(change) < 1) return '#adb5bd' // 保持不变
            return change > 0 ? '#40c057' : '#fa5252' // 上涨或下跌
          }
        }
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
    const response = await forecastApi.getPriceForecast()
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
    console.error('Error fetching price forecast data:', err)
    error.value = err.response?.data?.error || '获取价格预测数据失败'
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
.price-forecast {
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

.section-title {
  font-size: 1rem;
  margin-top: 0;
  margin-bottom: 16px;
  color: #24292e;
}

.price-recommendations {
  margin-top: 24px;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.recommendation-card {
  background-color: #f8f9fa;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e1e4e8;
  padding-bottom: 12px;
}

.clothing-type {
  font-weight: 600;
  font-size: 16px;
  color: #24292e;
}

.price-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommended-price {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-label {
  font-size: 14px;
  color: #586069;
}

.price-value {
  font-size: 24px;
  font-weight: 600;
  color: #24292e;
}

.price-comparison {
  display: flex;
  gap: 24px;
}

.current-avg-price,
.price-change {
  flex: 1;
}

.comparison-label {
  font-size: 12px;
  color: #6a737d;
  margin-bottom: 4px;
}

.comparison-value {
  font-size: 14px;
  font-weight: 500;
}

.recommendation-reason {
  font-size: 14px;
  color: #586069;
  padding-top: 12px;
  border-top: 1px solid #e1e4e8;
}

.increase {
  color: #28a745;
}

.decrease {
  color: #d73a49;
}

.neutral {
  color: #6a737d;
}

.price-analysis {
  margin-top: 24px;
}

.analysis-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.summary-item {
  flex: 1;
  min-width: 200px;
  background-color: #f8f9fa;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-label {
  font-size: 14px;
  color: #586069;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
  color: #24292e;
}
</style>
