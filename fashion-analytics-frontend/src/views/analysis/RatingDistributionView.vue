<template>
  <div class="rating-distribution">
    <div class="chart-header">
      <h2 class="chart-title">服装评价分布分析</h2>
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

      <div class="rating-summary">
        <h3 class="section-title">评价分析摘要</h3>
        <div class="summary-cards">
          <div class="summary-card positive">
            <div class="card-title">正面评价占比</div>
            <div class="card-value">{{ positiveRatingPercentage }}%</div>
            <div class="card-detail">
              <span class="rating-count">{{ positiveRatingCount }}</span> 条评价
            </div>
          </div>

          <div class="summary-card neutral">
            <div class="card-title">中性评价占比</div>
            <div class="card-value">{{ neutralRatingPercentage }}%</div>
            <div class="card-detail">
              <span class="rating-count">{{ neutralRatingCount }}</span> 条评价
            </div>
          </div>

          <div class="summary-card negative">
            <div class="card-title">负面评价占比</div>
            <div class="card-value">{{ negativeRatingPercentage }}%</div>
            <div class="card-detail">
              <span class="rating-count">{{ negativeRatingCount }}</span> 条评价
            </div>
          </div>

          <div class="summary-card">
            <div class="card-title">评价总数</div>
            <div class="card-value">{{ totalRatings }}</div>
            <div class="card-detail">所有评价类别总和</div>
          </div>
        </div>
      </div>

      <div class="data-table">
        <h3 class="table-title">评价分布明细</h3>
        <table class="rating-table">
          <thead>
            <tr>
              <th>评价类别</th>
              <th>评价数量</th>
              <th>占比 (%)</th>
              <th>情感倾向</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in ratingData" :key="index">
              <td>{{ item.rating_category }}</td>
              <td>{{ item.rating_count }}</td>
              <td>{{ item.percentage.toFixed(2) }}</td>
              <td>
                <span class="sentiment-indicator" :class="getSentimentClass(item.rating_category)">
                  {{ getSentimentText(item.rating_category) }}
                </span>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td><strong>总计</strong></td>
              <td>{{ totalRatings }}</td>
              <td>100.00%</td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="rating-insights">
        <h3 class="section-title">评价分析洞察</h3>

        <div class="insights-content">
          <div class="insight-card">
            <div class="insight-header">
              <i class="fas fa-lightbulb"></i>
              <span>总体评价情感</span>
            </div>
            <div class="insight-body">
              <p>{{ overallSentiment }}</p>
            </div>
          </div>

          <div class="insight-card" v-if="topPositiveCategory">
            <div class="insight-header">
              <i class="fas fa-thumbs-up"></i>
              <span>最受好评方面</span>
            </div>
            <div class="insight-body">
              <p><strong>{{ topPositiveCategory }}</strong> 是顾客最满意的方面，占正面评价的 {{ topPositiveCategoryPercentage }}%。建议继续保持这方面的优势。</p>
            </div>
          </div>

          <div class="insight-card" v-if="topNegativeCategory">
            <div class="insight-header">
              <i class="fas fa-thumbs-down"></i>
              <span>最需改进方面</span>
            </div>
            <div class="insight-body">
              <p><strong>{{ topNegativeCategory }}</strong> 是顾客最不满意的方面，占负面评价的 {{ topNegativeCategoryPercentage }}%。建议重点改进这方面的问题。</p>
            </div>
          </div>
        </div>
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
const ratingData = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 评价类别映射表（用于分类）
const sentimentMapping: Record<string, string> = {
  // 正面评价类别
  '质量好': 'positive',
  '款式时尚': 'positive',
  '物超所值': 'positive',
  '舒适': 'positive',
  '服务好': 'positive',
  '做工精细': 'positive',
  '材质优良': 'positive',
  // 中性评价类别
  '一般': 'neutral',
  '普通': 'neutral',
  '符合预期': 'neutral',
  '中规中矩': 'neutral',
  // 负面评价类别
  '质量差': 'negative',
  '不合身': 'negative',
  '价格贵': 'negative',
  '物流慢': 'negative',
  '色差大': 'negative',
  '尺码不准': 'negative',
  '做工粗糙': 'negative'
}

// 获取评价类别对应的情感倾向
const getSentimentClass = (category: string) => {
  return sentimentMapping[category] || 'neutral'
}

// 获取情感倾向文本
const getSentimentText = (category: string) => {
  const sentiment = sentimentMapping[category] || 'neutral'
  switch (sentiment) {
    case 'positive': return '正面'
    case 'negative': return '负面'
    default: return '中性'
  }
}

// 计算总评价数
const totalRatings = computed(() => {
  return ratingData.value.reduce((sum, item) => sum + item.rating_count, 0)
})

// 计算正面、中性、负面评价数量
const positiveRatingCount = computed(() => {
  return ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'positive')
    .reduce((sum, item) => sum + item.rating_count, 0)
})

const neutralRatingCount = computed(() => {
  return ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'neutral')
    .reduce((sum, item) => sum + item.rating_count, 0)
})

const negativeRatingCount = computed(() => {
  return ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'negative')
    .reduce((sum, item) => sum + item.rating_count, 0)
})

// 计算正面、中性、负面评价占比
const positiveRatingPercentage = computed(() => {
  if (totalRatings.value === 0) return 0
  return ((positiveRatingCount.value / totalRatings.value) * 100).toFixed(2)
})

const neutralRatingPercentage = computed(() => {
  if (totalRatings.value === 0) return 0
  return ((neutralRatingCount.value / totalRatings.value) * 100).toFixed(2)
})

const negativeRatingPercentage = computed(() => {
  if (totalRatings.value === 0) return 0
  return ((negativeRatingCount.value / totalRatings.value) * 100).toFixed(2)
})

// 获取最热门的正面评价类别
const topPositiveCategory = computed(() => {
  const positiveCategories = ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'positive')
    .sort((a, b) => b.rating_count - a.rating_count)

  return positiveCategories.length > 0 ? positiveCategories[0].rating_category : null
})

// 获取最热门的正面评价类别占比
const topPositiveCategoryPercentage = computed(() => {
  if (!topPositiveCategory.value || positiveRatingCount.value === 0) return 0

  const topCategory = ratingData.value.find(item => item.rating_category === topPositiveCategory.value)
  if (!topCategory) return 0

  return ((topCategory.rating_count / positiveRatingCount.value) * 100).toFixed(2)
})

// 获取最热门的负面评价类别
const topNegativeCategory = computed(() => {
  const negativeCategories = ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'negative')
    .sort((a, b) => b.rating_count - a.rating_count)

  return negativeCategories.length > 0 ? negativeCategories[0].rating_category : null
})

// 获取最热门的负面评价类别占比
const topNegativeCategoryPercentage = computed(() => {
  if (!topNegativeCategory.value || negativeRatingCount.value === 0) return 0

  const topCategory = ratingData.value.find(item => item.rating_category === topNegativeCategory.value)
  if (!topCategory) return 0

  return ((topCategory.rating_count / negativeRatingCount.value) * 100).toFixed(2)
})

// 获取总体评价情感
const overallSentiment = computed(() => {
  if (totalRatings.value === 0) return '暂无足够评价数据进行分析'

  const positivePercent = Number(positiveRatingPercentage.value)
  const negativePercent = Number(negativeRatingPercentage.value)

  if (positivePercent > 70) {
    return '顾客对产品整体评价非常正面，显示出高度的满意度。可以将这些正面反馈作为市场宣传的素材。'
  } else if (positivePercent > 50) {
    return '顾客对产品整体评价偏正面，大多数顾客表示满意。仍有改进空间，可关注负面评价类别。'
  } else if (positivePercent > 30 && negativePercent < 50) {
    return '顾客对产品评价中性偏正面，满意度处于一般水平。需要重点关注负面评价类别，提升整体满意度。'
  } else {
    return '顾客对产品评价偏负面，需要立即关注并解决反馈的问题。建议深入分析负面评价原因，并制定改进计划。'
  }
})

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

  const seriesData = ratingData.value.map(item => ({
    name: item.rating_category,
    value: item.rating_count,
    itemStyle: {
      color: getSentimentColor(item.rating_category)
    }
  }))

  console.log("313")
  console.log(seriesData)

  const option = {
    title: {
      text: '服装评价类别分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      type: 'scroll',
      maxHeight: 250
    },
    series: [
      {
        name: '评价类别',
        type: 'pie',
        radius: '55%',
        center: ['50%', '60%'],
        data: seriesData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
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

  // 按情感分类数据
  const positiveData = ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'positive')
    .sort((a, b) => b.rating_count - a.rating_count)

  const neutralData = ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'neutral')
    .sort((a, b) => b.rating_count - a.rating_count)

  const negativeData = ratingData.value
    .filter(item => getSentimentClass(item.rating_category) === 'negative')
    .sort((a, b) => b.rating_count - a.rating_count)

  // 合并数据，先正面，再中性，最后负面
  const sortedData = [...positiveData, ...neutralData, ...negativeData]

  const categories = sortedData.map(item => item.rating_category)
  const values = sortedData.map(item => item.rating_count)
  const colors = sortedData.map(item => getSentimentColor(item.rating_category))

  const option = {
    title: {
      text: '各评价类别数量分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '评价数量'
    },
    series: [
      {
        name: '评价数量',
        type: 'bar',
        data: values.map((value, index) => ({
          value,
          itemStyle: {
            color: colors[index]
          }
        })),
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        }
      }
    ]
  }

  barChart.setOption(option)
}

// 获取情感颜色
const getSentimentColor = (category: string) => {
  const sentiment = getSentimentClass(category)
  switch (sentiment) {
    case 'positive': return '#34a853'  // 绿色
    case 'negative': return '#ea4335'  // 红色
    default: return '#fbbc05'  // 黄色（中性）
  }
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await analysisApi.getRatingDistribution()
    console.log("API响应数据:", response.data)
    ratingData.value = response.data || []
    
    // 使用nextTick确保DOM已更新
    await nextTick()
    
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
    console.error('Error fetching rating distribution data:', err)
    error.value = err.response?.data?.error || '获取评价分布数据失败'
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
  ratingData.value = []
  
  // 重新获取数据
  fetchData()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.rating-distribution {
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

.rating-summary {
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
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.summary-card {
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.summary-card.positive {
  background-color: rgba(52, 168, 83, 0.1);
  border-color: rgba(52, 168, 83, 0.3);
}

.summary-card.neutral {
  background-color: rgba(251, 188, 5, 0.1);
  border-color: rgba(251, 188, 5, 0.3);
}

.summary-card.negative {
  background-color: rgba(234, 67, 53, 0.1);
  border-color: rgba(234, 67, 53, 0.3);
}

.card-title {
  font-size: 14px;
  color: #586069;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  color: #24292e;
  margin-bottom: 4px;
}

.summary-card.positive .card-value {
  color: #34a853;
}

.summary-card.neutral .card-value {
  color: #fbbc05;
}

.summary-card.negative .card-value {
  color: #ea4335;
}

.card-detail {
  font-size: 12px;
  color: #6a737d;
}

.rating-count {
  font-weight: 600;
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

.rating-table {
  width: 100%;
  border-collapse: collapse;
}

.rating-table th,
.rating-table td {
  border: 1px solid #e1e4e8;
  padding: 8px 12px;
  text-align: left;
}

.rating-table th {
  background-color: #f6f8fa;
  font-weight: 600;
  font-size: 14px;
}

.rating-table tbody tr:hover {
  background-color: #f6f8fa;
}

.rating-table tfoot {
  background-color: #f6f8fa;
  font-weight: 500;
}

.sentiment-indicator {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  text-align: center;
  min-width: 60px;
}

.sentiment-indicator.positive {
  background-color: #e6f4ea;
  color: #137333;
}

.sentiment-indicator.neutral {
  background-color: #fef7e0;
  color: #b06000;
}

.sentiment-indicator.negative {
  background-color: #fce8e6;
  color: #c5221f;
}

.rating-insights {
  margin-top: 24px;
}

.insights-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-card {
  background-color: #f1f8ff;
  border: 1px solid #c8e1ff;
  border-radius: 8px;
  padding: 16px;
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #0366d6;
  font-weight: 600;
  font-size: 16px;
}

.insight-body {
  color: #24292e;
  font-size: 14px;
  line-height: 1.5;
}

.insight-body p {
  margin: 0;
}

@media (max-width: 768px) {
  .pie-chart-area,
  .bar-chart-area {
    width: 100%;
  }
}
</style>
