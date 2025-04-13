<template>
  <div class="price-range-sales">
    <div class="chart-header">
      <h2 class="chart-title">服装价格区间销量分析</h2>
      <div class="chart-actions">
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          <i class="fas fa-sync-alt"></i> 刷新数据
        </button>
      </div>
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
      
      <div class="price-range-summary">
        <h3 class="section-title">价格区间分析摘要</h3>
        <div class="summary-cards">
          <div class="summary-card">
            <div class="card-title">最畅销价格区间</div>
            <div class="card-value">{{ bestSellingPriceRange }}</div>
            <div class="card-detail">销量占比：{{ (bestSellingPercentage).toFixed(2) }}%</div>
          </div>
          
          <div class="summary-card">
            <div class="card-title">最高销售额价格区间</div>
            <div class="card-value">{{ highestSalesValueRange }}</div>
            <div class="card-detail">销售额：{{ formatCurrency(highestSalesValue) }}元</div>
          </div>
          
          <div class="summary-card">
            <div class="card-title">平均客单价</div>
            <div class="card-value">{{ formatCurrency(averageOrderValue) }}元</div>
            <div class="card-detail">所有价格区间平均值</div>
          </div>
          
          <div class="summary-card">
            <div class="card-title">销量价格相关性</div>
            <div class="card-value">{{ priceVolumeCorrelation }}</div>
            <div class="card-detail">价格与销量的关系</div>
          </div>
        </div>
      </div>
      
      <div class="data-table">
        <h3 class="table-title">价格区间销量明细</h3>
        <table class="sales-table">
          <thead>
            <tr>
              <th>价格区间</th>
              <th>销售额 (元)</th>
              <th>订单数</th>
              <th>平均单价 (元)</th>
              <th>销量占比 (%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in priceRangeSalesData" :key="index">
              <td>{{ item.price_range_name }}</td>
              <td>{{ formatCurrency(item.total_sales) }}</td>
              <td>{{ item.order_count }}</td>
              <td>{{ formatCurrency(item.total_sales / item.order_count) }}</td>
              <td>{{ calculatePercentage(item.order_count) }}%</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td><strong>总计</strong></td>
              <td>{{ formatCurrency(totalSales) }}</td>
              <td>{{ totalOrders }}</td>
              <td>{{ formatCurrency(totalSales / totalOrders) }}</td>
              <td>100%</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { analysisApi } from '@/services/api'
import * as echarts from 'echarts'

// 图表容器引用
const chartContainer = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// 数据
const priceRangeSalesData = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 计算总销售额和订单数
const totalSales = computed(() => {
  return priceRangeSalesData.value.reduce((sum, item) => sum + Number(item.total_sales), 0)
})

const totalOrders = computed(() => {
  return priceRangeSalesData.value.reduce((sum, item) => sum + item.order_count, 0)
})

// 计算最畅销价格区间
const bestSellingPriceRange = computed(() => {
  if (priceRangeSalesData.value.length === 0) return '-'
  
  const sorted = [...priceRangeSalesData.value].sort((a, b) => b.order_count - a.order_count)
  return sorted[0].price_range_name
})

const bestSellingPercentage = computed(() => {
  if (priceRangeSalesData.value.length === 0 || totalOrders.value === 0) return 0
  
  const sorted = [...priceRangeSalesData.value].sort((a, b) => b.order_count - a.order_count)
  return (sorted[0].order_count / totalOrders.value) * 100
})

// 计算最高销售额价格区间
const highestSalesValueRange = computed(() => {
  if (priceRangeSalesData.value.length === 0) return '-'
  
  const sorted = [...priceRangeSalesData.value].sort((a, b) => b.total_sales - a.total_sales)
  return sorted[0].price_range_name
})

const highestSalesValue = computed(() => {
  if (priceRangeSalesData.value.length === 0) return 0
  
  const sorted = [...priceRangeSalesData.value].sort((a, b) => b.total_sales - a.total_sales)
  return sorted[0].total_sales
})

// 计算平均客单价
const averageOrderValue = computed(() => {
  if (totalOrders.value === 0) return 0
  return totalSales.value / totalOrders.value
})

// 确定价格与销量的相关性
const priceVolumeCorrelation = computed(() => {
  if (priceRangeSalesData.value.length < 3) return '数据不足'
  
  // 简单逻辑判断价格与销量的关系
  const sortedByPrice = [...priceRangeSalesData.value].sort((a, b) => {
    // 从价格区间名称中提取最低价格用于排序
    const extractMinPrice = (name: string) => {
      const match = name.match(/(\d+)/)
      return match ? parseInt(match[1]) : 0
    }
    
    return extractMinPrice(a.price_range_name) - extractMinPrice(b.price_range_name)
  })
  
  // 检查前半段和后半段的销量趋势
  const midIndex = Math.floor(sortedByPrice.length / 2)
  
  const firstHalfSales = sortedByPrice.slice(0, midIndex).reduce((sum, item) => sum + item.order_count, 0)
  const secondHalfSales = sortedByPrice.slice(midIndex).reduce((sum, item) => sum + item.order_count, 0)
  
  if (firstHalfSales > secondHalfSales * 1.5) {
    return '低价敏感'
  } else if (secondHalfSales > firstHalfSales * 1.5) {
    return '高价偏好'
  } else {
    return '价格不敏感'
  }
})

// 格式化货币
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
}

// 计算占比
const calculatePercentage = (value: number) => {
  if (totalOrders.value === 0) return 0
  return ((value / totalOrders.value) * 100).toFixed(2)
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
  
  // 提取价格区间的最小值进行排序（假设价格区间格式为 "xxxxx-xxxxx元" 或类似格式）
  const sortedData = [...priceRangeSalesData.value].sort((a, b) => {
    // 从价格区间名称中提取最低价格用于排序
    const extractMinPrice = (name: string) => {
      const match = name.match(/(\d+)/)
      return match ? parseInt(match[1]) : 0
    }
    
    return extractMinPrice(a.price_range_name) - extractMinPrice(b.price_range_name)
  })
  
  const ranges = sortedData.map(item => item.price_range_name)
  const sales = sortedData.map(item => item.total_sales)
  const orders = sortedData.map(item => item.order_count)
  const averagePrices = sortedData.map(item => 
    item.order_count > 0 ? item.total_sales / item.order_count : 0
  )
  
  const option = {
    title: {
      text: '服装价格区间销量分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params: any) {
        const range = params[0].axisValue
        const item = sortedData.find(d => d.price_range_name === range)
        
        if (!item) return ''
        
        const avgPrice = item.order_count > 0 ? item.total_sales / item.order_count : 0
        
        return `
          <div style="font-weight: bold; margin-bottom: 5px;">${range}</div>
          <div>销售额: ${formatCurrency(item.total_sales)} 元</div>
          <div>订单数: ${item.order_count}</div>
          <div>平均单价: ${formatCurrency(avgPrice)} 元</div>
          <div>占比: ${calculatePercentage(item.order_count)}%</div>
        `
      }
    },
    legend: {
      data: ['销售额', '订单数', '平均单价'],
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
      data: ranges,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '销售额',
        axisLabel: {
          formatter: '{value} 元'
        }
      },
      {
        type: 'value',
        name: '订单数',
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'bar',
        data: sales,
        itemStyle: {
          color: '#4285f4'
        }
      },
      {
        name: '订单数',
        type: 'line',
        yAxisIndex: 1,
        data: orders,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#ea4335'
        },
        lineStyle: {
          width: 2
        }
      },
      {
        name: '平均单价',
        type: 'line',
        data: averagePrices,
        symbol: 'triangle',
        symbolSize: 8,
        itemStyle: {
          color: '#34a853'
        },
        lineStyle: {
          width: 2,
          type: 'dashed'
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
    const response = await analysisApi.getPriceRangeSales()
    console.log("API响应数据:", response.data)
    priceRangeSalesData.value = response.data || []
    
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
    console.error('Error fetching price range sales data:', err)
    error.value = err.response?.data?.error || '获取价格区间销售数据失败'
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  console.log("强制刷新数据，清除缓存...")
  
  // 销毁现有图表以避免DOM冲突
  if (chart) {
    console.log("销毁现有图表")
    chart.dispose()
    chart = null
  }
  
  // 清空数据
  priceRangeSalesData.value = []
  
  // 重新获取数据
  fetchData()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.price-range-sales {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-title {
  margin: 0;
  font-size: 1.25rem;
  color: #24292e;
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

.price-range-summary {
  margin-top: 24px;
}

.section-title {
  font-size: 1rem;
  margin-top: 0;
  margin-bottom: 16px;
  color: #24292e;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.summary-card {
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.card-title {
  font-size: 14px;
  color: #586069;
  margin-bottom: 8px;
}

.card-value {
  font-size: 20px;
  font-weight: 600;
  color: #24292e;
  margin-bottom: 4px;
}

.card-detail {
  font-size: 12px;
  color: #6a737d;
}

.data-table {
  margin-top: 24px;
}

.table-title {
  font-size: 1rem;
  margin-top: 0;
  margin-bottom: 16px;
  color: #24292e;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
}

.sales-table th,
.sales-table td {
  border: 1px solid #e1e4e8;
  padding: 8px 12px;
  text-align: left;
}

.sales-table th {
  background-color: #f6f8fa;
  font-weight: 600;
  font-size: 14px;
}

.sales-table tbody tr:hover {
  background-color: #f6f8fa;
}

.sales-table tfoot {
  background-color: #f6f8fa;
  font-weight: 500;
}
</style>
