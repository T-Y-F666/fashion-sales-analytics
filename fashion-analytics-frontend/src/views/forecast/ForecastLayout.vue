<template>
  <div class="forecast-layout">
    <header class="forecast-header">
      <h1 class="forecast-title">预测分析</h1>
      <div class="tabs">
        <router-link :to="{ name: 'sales-forecast' }" class="tab-item">
          销量预测
        </router-link>
        <router-link :to="{ name: 'price-forecast' }" class="tab-item">
          价格预测
        </router-link>
      </div>
      <router-link :to="{ name: 'dashboard' }" class="back-link">
        返回仪表盘
      </router-link>
    </header>
    
    <div class="forecast-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
// 预测布局组件
</script>

<style scoped>
.forecast-layout {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.forecast-header {
  background-color: white;
  border-bottom: 1px solid #e1e4e8;
  padding: 16px 24px;
  position: relative;
}

.forecast-title {
  font-size: 1.5rem;
  margin: 0 0 16px 0;
  color: #24292e;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e1e4e8;
  padding-bottom: 16px;
}

.tab-item {
  margin-right: 24px;
  padding: 8px 0;
  color: #586069;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}

.tab-item:hover {
  color: #0366d6;
}

.tab-item.router-link-active {
  color: #0366d6;
  border-bottom-color: #0366d6;
}

.back-link {
  position: absolute;
  top: 16px;
  right: 24px;
  color: #0366d6;
  text-decoration: none;
  font-size: 14px;
}

.back-link:hover {
  text-decoration: underline;
}

.forecast-content {
  padding: 24px;
}
</style> 