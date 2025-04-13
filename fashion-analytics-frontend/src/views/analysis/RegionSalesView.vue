<template>
  <div class="region-sales">
    <div class="chart-header">
      <h2 class="chart-title">各地区销售数据分析</h2>
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

      <div class="data-table">
        <h3 class="table-title">销售数据明细</h3>
        <table class="sales-table">
          <thead>
            <tr>
              <th>地区</th>
              <th>销售额 (元)</th>
              <th>订单数</th>
              <th>占比</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in regionSalesData" :key="index">
              <td>{{ item.region_name }}</td>
              <td>{{ formatCurrency(item.total_sales) }}</td>
              <td>{{ item.order_count }}</td>
              <td>{{ calculatePercentage(item.total_sales) }}%</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td><strong>总计</strong></td>
              <td>{{ formatCurrency(totalSales) }}</td>
              <td>{{ totalOrders }}</td>
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
const regionSalesData = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 计算总销售额和订单数
const totalSales = computed(() => {
  return regionSalesData.value.reduce((sum, item) => sum + Number(item.total_sales), 0)
})

const totalOrders = computed(() => {
  return regionSalesData.value.reduce((sum, item) => sum + item.order_count, 0)
})

// 格式化货币
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
}

// 计算占比
const calculatePercentage = (value: number) => {
  if (totalSales.value === 0) return 0
  return ((value / totalSales.value) * 100).toFixed(2)
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

  const regions = regionSalesData.value.map(item => item.region_name)
  const sales = regionSalesData.value.map(item => item.total_sales)
  const orders = regionSalesData.value.map(item => item.order_count)


  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        const regionData = regionSalesData.value[params[0].dataIndex]
        return `
          <div style="font-weight: bold; margin-bottom: 5px;">${regionData.region_name}</div>
          <div>销售额: ${formatCurrency(regionData.total_sales)} 元</div>
          <div>订单数: ${regionData.order_count}</div>
          <div>占比: ${calculatePercentage(regionData.total_sales)}%</div>
        `
      }
    },
    legend: {
      data: ['销售额', '订单数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: regions,
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '销售额 (元)',
        axisLabel: {
          formatter: '{value}'
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
          color: '#34a853'
        },
        lineStyle: {
          width: 2
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
    const response = await analysisApi.getRegionSales()
    console.log("API响应数据:", response.data)
    regionSalesData.value = response.data || []

    // 使用nextTick确保DOM已更新
    await nextTick()
    
    if (chart) {
      console.log("更新现有图表")
      updateChart()
    } else {
      console.log("初始化新图表")
      setTimeout(() => {
        initChart()
      }, 100) // 添加小延迟以确保DOM完全渲染
    }
  } catch (err: any) {
    console.error('Error fetching region sales data:', err)
    error.value = err.response?.data?.error || '获取地区销售数据失败'
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
  regionSalesData.value = []
  
  // 重新获取数据
  fetchData()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.region-sales {
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

.data-table {
  margin-top: 16px;
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
