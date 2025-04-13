<template>
  <div class="clothing-type-sales">
    <div class="chart-header">
      <h2 class="chart-title">服装类型销售占比分析</h2>
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
      <div class="chart-flex">
        <div class="pie-chart-area" ref="pieChartContainer"></div>
        <div class="bar-chart-area" ref="barChartContainer"></div>
      </div>
      
      <div class="data-table">
        <h3 class="table-title">服装类型销售明细</h3>
        <table class="sales-table">
          <thead>
            <tr>
              <th>服装类型</th>
              <th>销售额 (元)</th>
              <th>订单数</th>
              <th>占比 (%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in typeSalesData" :key="index">
              <td>{{ item.clothing_type_name }}</td>
              <td>{{ formatCurrency(item.total_sales) }}</td>
              <td>{{ item.order_count }}</td>
              <td>{{ item.percentage.toFixed(2) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td><strong>总计</strong></td>
              <td>{{ formatCurrency(totalSales) }}</td>
              <td>{{ totalOrders }}</td>
              <td>100.00</td>
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
const pieChartContainer = ref<HTMLElement | null>(null)
const barChartContainer = ref<HTMLElement | null>(null)
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

// 数据
const typeSalesData = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 计算总销售额和订单数
const totalSales = computed(() => {
  return typeSalesData.value.reduce((sum, item) => sum + Number(item.total_sales), 0)
})

const totalOrders = computed(() => {
  return typeSalesData.value.reduce((sum, item) => sum + item.order_count, 0)
})

// 格式化货币
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
}

// 初始化饼图
const initPieChart = () => {
  console.log('initPieChart函数被调用')
  console.log('pieChartContainer.value:', pieChartContainer.value)
  
  if (!pieChartContainer.value) {
    console.error('饼图容器元素未找到!')
    return
  }
  
  console.log('开始初始化饼图ECharts实例')
  pieChart = echarts.init(pieChartContainer.value)
  updatePieChart()
  
  window.addEventListener('resize', () => {
    pieChart?.resize()
  })
}

// 更新饼图数据
const updatePieChart = () => {
  if (!pieChart) return
  
  const seriesData = typeSalesData.value.map(item => ({
    name: item.clothing_type_name,
    value: item.total_sales
  }))
  
  const option = {
    title: {
      text: '服装类型销售额占比',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params: any) {
        const item = typeSalesData.value.find(i => i.clothing_type_name === params.name)
        return `
          <div style="font-weight: bold; margin-bottom: 5px;">${params.name}</div>
          <div>销售额: ${formatCurrency(params.value)} 元</div>
          <div>占比: ${params.percent}%</div>
          <div>订单数: ${item ? item.order_count : 0}</div>
        `
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      type: 'scroll',
      maxHeight: 250
    },
    series: [
      {
        name: '销售额',
        type: 'pie',
        radius: '55%',
        center: ['50%', '50%'],
        data: seriesData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}: {d}%'
        }
      }
    ]
  }
  
  pieChart.setOption(option)
}

// 初始化柱状图
const initBarChart = () => {
  console.log('initBarChart函数被调用')
  console.log('barChartContainer.value:', barChartContainer.value)
  
  if (!barChartContainer.value) {
    console.error('柱状图容器元素未找到!')
    return
  }
  
  console.log('开始初始化柱状图ECharts实例')
  barChart = echarts.init(barChartContainer.value)
  updateBarChart()
  
  window.addEventListener('resize', () => {
    barChart?.resize()
  })
}

// 更新柱状图数据
const updateBarChart = () => {
  if (!barChart) return
  
  // 按销售额降序排序
  const sortedData = [...typeSalesData.value].sort((a, b) => b.total_sales - a.total_sales)
  
  const types = sortedData.map(item => item.clothing_type_name)
  const sales = sortedData.map(item => item.total_sales)
  const orders = sortedData.map(item => item.order_count)
  
  const option = {
    title: {
      text: '服装类型销售额与订单数',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['销售额', '订单数'],
      top: 'bottom'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '15%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: types,
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
        type: 'bar',
        yAxisIndex: 1,
        data: orders,
        itemStyle: {
          color: '#ea4335'
        }
      }
    ]
  }
  
  barChart.setOption(option)
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await analysisApi.getClothingTypeSales()
    console.log("API响应数据:", response.data)
    typeSalesData.value = response.data || []
    
    // 使用nextTick确保DOM已更新
    await nextTick()
    
    // 初始化图表
    setTimeout(() => {
      if (pieChart) {
        console.log("更新现有饼图")
        updatePieChart()
      } else {
        console.log("初始化新饼图")
        initPieChart()
      }
      
      if (barChart) {
        console.log("更新现有柱状图")
        updateBarChart()
      } else {
        console.log("初始化新柱状图")
        initBarChart()
      }
    }, 100) // 添加小延迟以确保DOM完全渲染
  } catch (err: any) {
    console.error('Error fetching clothing type sales data:', err)
    error.value = err.response?.data?.error || '获取服装类型销售数据失败'
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  console.log("强制刷新数据，清除缓存...")
  
  // 销毁现有图表以避免DOM冲突
  if (pieChart) {
    console.log("销毁现有饼图")
    pieChart.dispose()
    pieChart = null
  }
  
  if (barChart) {
    console.log("销毁现有柱状图")
    barChart.dispose()
    barChart = null
  }
  
  // 清空数据
  typeSalesData.value = []
  
  // 重新获取数据
  fetchData()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.clothing-type-sales {
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

.chart-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.pie-chart-area {
  width: calc(50% - 12px);
  min-width: 300px;
  height: 400px;
  flex-grow: 1;
}

.bar-chart-area {
  width: calc(50% - 12px);
  min-width: 300px;
  height: 400px;
  flex-grow: 1;
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

@media (max-width: 768px) {
  .pie-chart-area,
  .bar-chart-area {
    width: 100%;
  }
}
</style> 