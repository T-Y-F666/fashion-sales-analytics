<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1 class="dashboard-title">服装销售数据分析与预测系统</h1>
      <div class="user-info">
        <span>{{ username }}</span>
        <button @click="logout" class="logout-btn">退出登录</button>
      </div>
    </header>
    
    <div class="dashboard-content">
      <aside class="dashboard-sidebar">
        <nav class="nav-menu">
          <div class="nav-section">
            <h3 class="nav-title">数据分析</h3>
            <ul class="nav-items">
              <li>
                <router-link :to="{ name: 'region-sales' }">
                  地区销售分析
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'clothing-type-sales' }">
                  服装类型占比
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'price-range-sales' }">
                  价格区间销量
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'rating-distribution' }">
                  服装评价分析
                </router-link>
              </li>
            </ul>
          </div>
          
          <div class="nav-section">
            <h3 class="nav-title">预测分析</h3>
            <ul class="nav-items">
              <li>
                <router-link :to="{ name: 'sales-forecast' }">
                  销量预测
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'price-forecast' }">
                  价格预测
                </router-link>
              </li>
            </ul>
          </div>
        </nav>
      </aside>
      
      <main class="dashboard-main">
        <div class="dashboard-summary">
          <h2 class="section-title">系统概览</h2>
          
          <div class="summary-cards">
            <div class="summary-card">
              <div class="card-icon">
                <i class="fas fa-map-marker-alt"></i>
              </div>
              <div class="card-content">
                <div class="card-title">地区分析</div>
                <div class="card-description">查看各地区销售情况</div>
                <router-link :to="{ name: 'region-sales' }" class="card-link">
                  查看详情
                </router-link>
              </div>
            </div>
            
            <div class="summary-card">
              <div class="card-icon">
                <i class="fas fa-tshirt"></i>
              </div>
              <div class="card-content">
                <div class="card-title">类型分析</div>
                <div class="card-description">查看各类服装销售占比</div>
                <router-link :to="{ name: 'clothing-type-sales' }" class="card-link">
                  查看详情
                </router-link>
              </div>
            </div>
            
            <div class="summary-card">
              <div class="card-icon">
                <i class="fas fa-tags"></i>
              </div>
              <div class="card-content">
                <div class="card-title">价格分析</div>
                <div class="card-description">查看各价格区间销量</div>
                <router-link :to="{ name: 'price-range-sales' }" class="card-link">
                  查看详情
                </router-link>
              </div>
            </div>
            
            <div class="summary-card">
              <div class="card-icon">
                <i class="fas fa-star"></i>
              </div>
              <div class="card-content">
                <div class="card-title">评价分析</div>
                <div class="card-description">查看服装评价分布</div>
                <router-link :to="{ name: 'rating-distribution' }" class="card-link">
                  查看详情
                </router-link>
              </div>
            </div>
          </div>
          
          <div class="forecast-section">
            <h2 class="section-title">预测分析</h2>
            
            <div class="forecast-cards">
              <div class="forecast-card">
                <div class="card-icon">
                  <i class="fas fa-chart-line"></i>
                </div>
                <div class="card-content">
                  <div class="card-title">销量预测</div>
                  <div class="card-description">基于历史数据预测未来销量趋势</div>
                  <router-link :to="{ name: 'sales-forecast' }" class="card-link">
                    查看预测
                  </router-link>
                </div>
              </div>
              
              <div class="forecast-card">
                <div class="card-icon">
                  <i class="fas fa-dollar-sign"></i>
                </div>
                <div class="card-content">
                  <div class="card-title">价格预测</div>
                  <div class="card-description">基于销售数据推荐最优价格</div>
                  <router-link :to="{ name: 'price-forecast' }" class="card-link">
                    查看预测
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = computed(() => {
  return authStore.user ? authStore.user.username : '用户'
})

const logout = async () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #4285f4;
  color: white;
}

.dashboard-title {
  font-size: 1.5rem;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logout-btn {
  padding: 6px 12px;
  background-color: transparent;
  border: 1px solid white;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.dashboard-content {
  display: flex;
  flex: 1;
}

.dashboard-sidebar {
  width: 240px;
  background-color: white;
  border-right: 1px solid #e1e4e8;
  padding: 20px 0;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-title {
  padding: 0 20px;
  font-size: 14px;
  font-weight: 600;
  color: #586069;
  margin-bottom: 8px;
}

.nav-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-items li a {
  display: block;
  padding: 8px 20px;
  color: #24292e;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.2s;
}

.nav-items li a:hover,
.nav-items li a.router-link-active {
  background-color: #f1f8ff;
  color: #0366d6;
}

.dashboard-main {
  flex: 1;
  padding: 24px;
}

.section-title {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 1.25rem;
  color: #24292e;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 36px;
}

.summary-card, .forecast-card {
  display: flex;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.summary-card:hover, .forecast-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #4285f4;
  color: white;
  font-size: 24px;
}

.card-content {
  flex: 1;
  padding: 16px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 8px;
  color: #24292e;
}

.card-description {
  font-size: 14px;
  color: #586069;
  margin-bottom: 12px;
}

.card-link {
  display: inline-block;
  font-size: 14px;
  color: #0366d6;
  text-decoration: none;
}

.card-link:hover {
  text-decoration: underline;
}

.forecast-section {
  margin-top: 36px;
}

.forecast-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}
</style> 