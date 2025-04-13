from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Region, ClothingType, PriceRange, RatingCategory, 
    Clothing, SalesOrder, OrderItem, Rating
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class ClothingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingType
        fields = '__all__'

class PriceRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceRange
        fields = '__all__'

class RatingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingCategory
        fields = '__all__'

class ClothingSerializer(serializers.ModelSerializer):
    clothing_type_name = serializers.ReadOnlyField(source='clothing_type.name')
    price_range_name = serializers.ReadOnlyField(source='price_range.name')
    
    class Meta:
        model = Clothing
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    clothing_name = serializers.ReadOnlyField(source='clothing.name')
    
    class Meta:
        model = OrderItem
        fields = '__all__'

class SalesOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.ReadOnlyField(source='user.username')
    region_name = serializers.ReadOnlyField(source='region.name')
    
    class Meta:
        model = SalesOrder
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    clothing_name = serializers.ReadOnlyField(source='clothing.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Rating
        fields = '__all__'

# 统计分析数据序列化器
class RegionSalesSerializer(serializers.Serializer):
    region_name = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    order_count = serializers.IntegerField()

class ClothingTypeSalesSerializer(serializers.Serializer):
    clothing_type_name = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    order_count = serializers.IntegerField()
    percentage = serializers.FloatField()

class PriceRangeSalesSerializer(serializers.Serializer):
    price_range_name = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    order_count = serializers.IntegerField()

class RatingDistributionSerializer(serializers.Serializer):
    rating_category = serializers.CharField()
    rating_count = serializers.IntegerField()
    percentage = serializers.FloatField()

class SalesForecastSerializer(serializers.Serializer):
    date = serializers.DateField()
    forecasted_sales = serializers.FloatField()
    
class PriceForecastSerializer(serializers.Serializer):
    clothing_type = serializers.CharField()
    forecasted_price = serializers.FloatField() 