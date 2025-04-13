from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import random

from .models import (
    Region, ClothingType, PriceRange, RatingCategory, 
    Clothing, SalesOrder, OrderItem, Rating
)
from .serializers import (
    UserSerializer, RegionSerializer, ClothingTypeSerializer,
    PriceRangeSerializer, RatingCategorySerializer, ClothingSerializer,
    SalesOrderSerializer, OrderItemSerializer, RatingSerializer,
    RegionSalesSerializer, ClothingTypeSalesSerializer,
    PriceRangeSalesSerializer, RatingDistributionSerializer,
    SalesForecastSerializer, PriceForecastSerializer
)

# Create your views here.

# 用户登录注册视图
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': '成功登出'}, status=status.HTTP_200_OK)

# 基础数据视图集
class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClothingTypeViewSet(viewsets.ModelViewSet):
    queryset = ClothingType.objects.all()
    serializer_class = ClothingTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class PriceRangeViewSet(viewsets.ModelViewSet):
    queryset = PriceRange.objects.all()
    serializer_class = PriceRangeSerializer
    permission_classes = [permissions.IsAuthenticated]

class RatingCategoryViewSet(viewsets.ModelViewSet):
    queryset = RatingCategory.objects.all()
    serializer_class = RatingCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ClothingViewSet(viewsets.ModelViewSet):
    queryset = Clothing.objects.all()
    serializer_class = ClothingSerializer
    permission_classes = [permissions.IsAuthenticated]

class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

# 数据分析视图
class RegionSalesAnalysisView(APIView):
    """各地区销售数据柱状图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 聚合各地区的销售数据
        region_sales = SalesOrder.objects.values(
            'region__name'
        ).annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_sales')
        
        # 序列化结果
        result = []
        for item in region_sales:
            result.append({
                'region_name': item['region__name'],
                'total_sales': item['total_sales'],
                'order_count': item['order_count']
            })
        
        serializer = RegionSalesSerializer(result, many=True)
        return Response(serializer.data)

class ClothingTypeSalesAnalysisView(APIView):
    """服装销售类型占比饼图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 通过订单条目获取各类型服装的销售数据
        type_sales = OrderItem.objects.values(
            'clothing__clothing_type__name'
        ).annotate(
            total_sales=Sum(F('price') * F('quantity')),
            order_count=Count('id')
        ).order_by('-total_sales')
        
        # 计算总销售额用于计算占比
        total_sales_amount = OrderItem.objects.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0
        
        # 序列化结果
        result = []
        for item in type_sales:
            percentage = 0
            if total_sales_amount > 0:
                percentage = float(item['total_sales']) / float(total_sales_amount) * 100
                
            result.append({
                'clothing_type_name': item['clothing__clothing_type__name'],
                'total_sales': item['total_sales'],
                'order_count': item['order_count'],
                'percentage': round(percentage, 2)
            })
        
        serializer = ClothingTypeSalesSerializer(result, many=True)
        return Response(serializer.data)

class PriceRangeSalesAnalysisView(APIView):
    """服装价格区间销量折线图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 通过订单条目获取各价格区间的销售数据
        price_range_sales = OrderItem.objects.values(
            'clothing__price_range__name'
        ).annotate(
            total_sales=Sum(F('price') * F('quantity')),
            order_count=Count('id')
        ).order_by('clothing__price_range__min_price')
        
        # 序列化结果
        result = []
        for item in price_range_sales:
            if item['clothing__price_range__name']:  # 确保价格区间不为空
                result.append({
                    'price_range_name': item['clothing__price_range__name'],
                    'total_sales': item['total_sales'],
                    'order_count': item['order_count']
                })
        
        serializer = PriceRangeSalesSerializer(result, many=True)
        return Response(serializer.data)

class RatingDistributionView(APIView):
    """服装评价饼图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取各评价类别的分布
        rating_distribution = Rating.objects.values(
            'category__name'
        ).annotate(
            rating_count=Count('id')
        ).order_by('-rating_count')
        
        # 计算评价总数用于计算占比
        total_ratings = Rating.objects.count()
        
        # 序列化结果
        result = []
        for item in rating_distribution:
            if item['category__name']:  # 确保评价类别不为空
                percentage = 0
                if total_ratings > 0:
                    percentage = float(item['rating_count']) / float(total_ratings) * 100
                    
                result.append({
                    'rating_category': item['category__name'],
                    'rating_count': item['rating_count'],
                    'percentage': round(percentage, 2)
                })
        
        serializer = RatingDistributionSerializer(result, many=True)
        return Response(serializer.data)

# 预测分析视图
class SalesForecastView(APIView):
    """销量预测"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取历史销售数据
        sales_data = SalesOrder.objects.values('order_date').annotate(
            daily_sales=Sum('total_amount')
        ).order_by('order_date')
        
        # 如果数据不足，返回错误
        if len(sales_data) < 30:
            return Response(
                {'error': '历史数据不足，无法进行准确预测'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 转换为DataFrame用于预测
        df = pd.DataFrame(sales_data)
        
        # 特征工程
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['day_of_week'] = df['order_date'].dt.dayofweek
        df['month'] = df['order_date'].dt.month
        df['year'] = df['order_date'].dt.year
        df['day'] = df['order_date'].dt.day
        
        # 创建训练数据
        X = df[['day_of_week', 'month', 'year', 'day']].values
        y = df['daily_sales'].values
        
        # 标准化特征
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 训练线性回归模型
        model = LinearRegression()
        model.fit(X_scaled, y)
        
        # 预测未来30天的销售额
        future_dates = []
        future_predictions = []
        
        last_date = df['order_date'].max()
        
        # 获取历史平均销售额
        avg_sales = df['daily_sales'].mean()
        
        # 添加周期性波动和随机因素，使预测更加真实
        for i in range(1, 31):
            future_date = last_date + timedelta(days=i)
            future_dates.append(future_date)
            
            # 构建特征
            features = np.array([
                future_date.dayofweek,
                future_date.month,
                future_date.year,
                future_date.day
            ]).reshape(1, -1)
            
            # 标准化特征
            features_scaled = scaler.transform(features)
            
            # 基础预测
            base_prediction = model.predict(features_scaled)[0]
            
            # 添加周期性波动 (星期几影响)
            weekday_effect = 1.0
            if future_date.weekday() >= 5:  # 周末
                weekday_effect = 1.2  # 周末销售额提高20%
            
            # 添加一些随机波动，使预测更加自然
            random_factor = 0.85 + random.random() * 0.3  # 0.85到1.15之间的随机数
            
            # 最终预测结果
            prediction = base_prediction * weekday_effect * random_factor
            
            # 确保预测值合理
            if prediction < 0:
                prediction = avg_sales * 0.5  # 使用历史平均销售额的一半作为下限
                
            future_predictions.append(prediction)
        
        # 构建结果
        result = []
        for date, prediction in zip(future_dates, future_predictions):
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'forecasted_sales': round(float(prediction), 2)
            })
        
        serializer = SalesForecastSerializer(result, many=True)
        return Response(serializer.data)

class PriceForecastView(APIView):
    """价格预测"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取历史价格数据
        price_data = Clothing.objects.values('clothing_type__name').annotate(
            avg_price=Avg('price')
        ).order_by('clothing_type__name')
        
        # 结合销量数据
        sales_data = OrderItem.objects.values('clothing__clothing_type__name').annotate(
            total_quantity=Sum('quantity'),
            avg_sold_price=Avg('price')
        ).order_by('clothing__clothing_type__name')
        
        # 合并数据
        combined_data = {}
        for item in price_data:
            type_name = item['clothing_type__name']
            combined_data[type_name] = {
                'avg_price': item['avg_price'],
                'total_quantity': 0,
                'avg_sold_price': 0
            }
            
        for item in sales_data:
            type_name = item['clothing__clothing_type__name']
            if type_name in combined_data:
                combined_data[type_name]['total_quantity'] = item['total_quantity']
                combined_data[type_name]['avg_sold_price'] = item['avg_sold_price']
        
        # 预测最佳价格 (简单算法：如果销量高且平均售价高于当前价格，建议提高价格)
        result = []
        for type_name, data in combined_data.items():
            forecasted_price = data['avg_price']
            
            # 简单的价格预测逻辑
            if data['total_quantity'] > 100 and data['avg_sold_price'] > data['avg_price']:
                # 建议提高价格
                forecasted_price = float(data['avg_sold_price']) * 1.05
            elif data['total_quantity'] < 50 and data['avg_sold_price'] < data['avg_price']:
                # 建议降低价格
                forecasted_price = float(data['avg_sold_price']) * 0.95
            
            result.append({
                'clothing_type': type_name,
                'forecasted_price': round(float(forecasted_price), 2)
            })
        
        serializer = PriceForecastSerializer(result, many=True)
        return Response(serializer.data)
