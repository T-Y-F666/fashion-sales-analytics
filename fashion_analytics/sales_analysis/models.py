from django.db import models
from django.contrib.auth.models import User

class Region(models.Model):
    """地区模型"""
    name = models.CharField(max_length=50, verbose_name="地区名称")
    code = models.CharField(max_length=20, verbose_name="地区代码")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "地区"
        verbose_name_plural = verbose_name

class ClothingType(models.Model):
    """服装类型模型"""
    name = models.CharField(max_length=50, verbose_name="类型名称")
    description = models.TextField(blank=True, null=True, verbose_name="类型描述")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "服装类型"
        verbose_name_plural = verbose_name

class PriceRange(models.Model):
    """价格区间模型"""
    name = models.CharField(max_length=50, verbose_name="区间名称")
    min_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="最低价")
    max_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="最高价")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "价格区间"
        verbose_name_plural = verbose_name

class RatingCategory(models.Model):
    """评价类别模型"""
    name = models.CharField(max_length=50, verbose_name="评价类别")
    description = models.TextField(blank=True, null=True, verbose_name="评价描述")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "评价类别"
        verbose_name_plural = verbose_name

class Clothing(models.Model):
    """服装商品模型"""
    name = models.CharField(max_length=100, verbose_name="商品名称")
    clothing_type = models.ForeignKey(ClothingType, on_delete=models.CASCADE, verbose_name="服装类型")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    price_range = models.ForeignKey(PriceRange, on_delete=models.SET_NULL, null=True, verbose_name="价格区间")
    description = models.TextField(blank=True, null=True, verbose_name="商品描述")
    image = models.ImageField(upload_to='clothing_images/', blank=True, null=True, verbose_name="商品图片")
    stock = models.IntegerField(default=0, verbose_name="库存量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "服装商品"
        verbose_name_plural = verbose_name

class SalesOrder(models.Model):
    """销售订单模型"""
    order_number = models.CharField(max_length=50, unique=True, verbose_name="订单编号")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="地区")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单总额")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="订单日期")
    
    def __str__(self):
        return self.order_number
    
    class Meta:
        verbose_name = "销售订单"
        verbose_name_plural = verbose_name

class OrderItem(models.Model):
    """订单条目模型"""
    order = models.ForeignKey(SalesOrder, related_name='items', on_delete=models.CASCADE, verbose_name="订单")
    clothing = models.ForeignKey(Clothing, on_delete=models.CASCADE, verbose_name="服装商品")
    quantity = models.PositiveIntegerField(default=1, verbose_name="数量")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    
    def __str__(self):
        return f"{self.order.order_number} - {self.clothing.name}"
    
    class Meta:
        verbose_name = "订单条目"
        verbose_name_plural = verbose_name

class Rating(models.Model):
    """商品评价模型"""
    RATING_CHOICES = (
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    clothing = models.ForeignKey(Clothing, on_delete=models.CASCADE, verbose_name="服装商品")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="评分")
    comment = models.TextField(blank=True, null=True, verbose_name="评价内容")
    category = models.ForeignKey(RatingCategory, on_delete=models.SET_NULL, null=True, verbose_name="评价类别")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评价时间")
    
    def __str__(self):
        return f"{self.user.username} - {self.clothing.name} - {self.rating}星"
    
    class Meta:
        verbose_name = "商品评价"
        verbose_name_plural = verbose_name
