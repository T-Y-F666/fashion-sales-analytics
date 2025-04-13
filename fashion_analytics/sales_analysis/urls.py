from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'clothing-types', views.ClothingTypeViewSet)
router.register(r'price-ranges', views.PriceRangeViewSet)
router.register(r'rating-categories', views.RatingCategoryViewSet)
router.register(r'clothing', views.ClothingViewSet)
router.register(r'sales-orders', views.SalesOrderViewSet)
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'ratings', views.RatingViewSet)

urlpatterns = [
    # 基础API路由
    path('', include(router.urls)),
    
    # 用户认证路由
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # 数据分析路由
    path('analysis/region-sales/', views.RegionSalesAnalysisView.as_view(), name='region-sales'),
    path('analysis/clothing-type-sales/', views.ClothingTypeSalesAnalysisView.as_view(), name='clothing-type-sales'),
    path('analysis/price-range-sales/', views.PriceRangeSalesAnalysisView.as_view(), name='price-range-sales'),
    path('analysis/rating-distribution/', views.RatingDistributionView.as_view(), name='rating-distribution'),
    
    # 预测分析路由
    path('forecast/sales/', views.SalesForecastView.as_view(), name='sales-forecast'),
    path('forecast/price/', views.PriceForecastView.as_view(), name='price-forecast'),
] 