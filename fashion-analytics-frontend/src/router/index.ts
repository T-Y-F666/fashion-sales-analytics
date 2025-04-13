import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/dashboard',
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { guest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/dashboard/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('../views/analysis/AnalysisLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'region-sales',
          name: 'region-sales',
          component: () => import('../views/analysis/RegionSalesView.vue'),
        },
        {
          path: 'clothing-type-sales',
          name: 'clothing-type-sales',
          component: () => import('../views/analysis/ClothingTypeSalesView.vue'),
        },
        {
          path: 'price-range-sales',
          name: 'price-range-sales',
          component: () => import('../views/analysis/PriceRangeSalesView.vue'),
        },
        {
          path: 'rating-distribution',
          name: 'rating-distribution',
          component: () => import('../views/analysis/RatingDistributionView.vue'),
        }
      ]
    },
    {
      path: '/forecast',
      name: 'forecast',
      component: () => import('../views/forecast/ForecastLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'sales',
          name: 'sales-forecast',
          component: () => import('../views/forecast/SalesForecastView.vue'),
        },
        {
          path: 'price',
          name: 'price-forecast',
          component: () => import('../views/forecast/PriceForecastView.vue'),
        }
      ]
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isLoggedIn = authStore.isLoggedIn
  
  // 需要认证的路由
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      next({ name: 'login' })
    } else {
      next()
    }
  } 
  // 游客路由（已登录用户重定向到首页）
  else if (to.matched.some(record => record.meta.guest)) {
    if (isLoggedIn) {
      next({ name: 'dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
