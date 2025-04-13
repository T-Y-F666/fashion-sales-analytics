from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from sales_analysis.models import (
    Region, ClothingType, PriceRange, RatingCategory,
    Clothing, SalesOrder, OrderItem, Rating
)
from django.db import transaction
from django.utils import timezone
import random
import datetime
import uuid

class Command(BaseCommand):
    help = '为时尚销售分析系统生成演示数据'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('开始生成演示数据...')
        
        # 创建管理员用户
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('创建管理员用户成功'))
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write('管理员用户已存在')
        
        # 创建普通用户
        test_users = []
        for i in range(1, 11):
            username = f'user{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'user{i}@example.com',
                    password='password123'
                )
                test_users.append(user)
                self.stdout.write(f'创建用户 {username} 成功')
            else:
                test_users.append(User.objects.get(username=username))
                self.stdout.write(f'用户 {username} 已存在')
        
        # 创建地区数据
        regions_data = [
            {'name': '华东地区', 'code': 'EAST'},
            {'name': '华南地区', 'code': 'SOUTH'},
            {'name': '华北地区', 'code': 'NORTH'},
            {'name': '华中地区', 'code': 'CENTRAL'},
            {'name': '西南地区', 'code': 'SOUTHWEST'},
            {'name': '西北地区', 'code': 'NORTHWEST'},
            {'name': '东北地区', 'code': 'NORTHEAST'},
        ]
        
        regions = []
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(**region_data)
            regions.append(region)
            status = '创建' if created else '已存在'
            self.stdout.write(f'地区 {region.name} {status}')
        
        # 创建服装类型数据
        clothing_types_data = [
            {'name': 'T恤', 'description': '简约舒适的休闲T恤'},
            {'name': '衬衫', 'description': '正式场合的必备单品'},
            {'name': '裤子', 'description': '各类裤装，包括牛仔裤、休闲裤等'},
            {'name': '外套', 'description': '秋冬季节的保暖外套'},
            {'name': '裙装', 'description': '女性优雅的裙装系列'},
            {'name': '西装', 'description': '商务职场的正装西服'},
            {'name': '运动装', 'description': '运动健身的专业装备'},
            {'name': '内衣', 'description': '贴身舒适的内衣系列'},
            {'name': '配饰', 'description': '时尚搭配的各类配饰'},
        ]
        
        clothing_types = []
        for type_data in clothing_types_data:
            clothing_type, created = ClothingType.objects.get_or_create(**type_data)
            clothing_types.append(clothing_type)
            status = '创建' if created else '已存在'
            self.stdout.write(f'服装类型 {clothing_type.name} {status}')
        
        # 创建价格区间数据
        price_ranges_data = [
            {'name': '低价区间', 'min_price': 0, 'max_price': 100},
            {'name': '中低价区间', 'min_price': 100, 'max_price': 300},
            {'name': '中价区间', 'min_price': 300, 'max_price': 500},
            {'name': '中高价区间', 'min_price': 500, 'max_price': 1000},
            {'name': '高价区间', 'min_price': 1000, 'max_price': 99999},
        ]
        
        price_ranges = []
        for range_data in price_ranges_data:
            price_range, created = PriceRange.objects.get_or_create(**range_data)
            price_ranges.append(price_range)
            status = '创建' if created else '已存在'
            self.stdout.write(f'价格区间 {price_range.name} {status}')
        
        # 创建评价类别数据
        rating_categories_data = [
            {'name': '质量好评', 'description': '产品质量优良'},
            {'name': '性价比高', 'description': '价格合理，物有所值'},
            {'name': '款式时尚', 'description': '设计新颖，款式时尚'},
            {'name': '舒适度佳', 'description': '穿着舒适，体验良好'},
            {'name': '做工精细', 'description': '做工精良，细节处理好'},
            {'name': '物流快速', 'description': '配送迅速，包装完好'},
            {'name': '服务满意', 'description': '售前售后服务态度好'},
            {'name': '质量差评', 'description': '产品质量不佳'},
            {'name': '尺码偏差', 'description': '尺码与描述不符'},
            {'name': '色差严重', 'description': '颜色与图片不符'},
        ]
        
        rating_categories = []
        for category_data in rating_categories_data:
            category, created = RatingCategory.objects.get_or_create(**category_data)
            rating_categories.append(category)
            status = '创建' if created else '已存在'
            self.stdout.write(f'评价类别 {category.name} {status}')
        
        # 创建服装商品数据
        if Clothing.objects.count() < 30:  # 避免重复创建太多商品
            clothing_items = []
            
            # T恤
            t_shirt_names = ['基础纯色T恤', '印花图案T恤', '条纹T恤', 'Polo衫', '宽松T恤']
            for name in t_shirt_names:
                price = random.randint(50, 300)
                price_range = next((pr for pr in price_ranges if pr.min_price <= price <= pr.max_price), price_ranges[0])
                clothing = Clothing.objects.create(
                    name=name,
                    clothing_type=next(ct for ct in clothing_types if ct.name == 'T恤'),
                    price=price,
                    price_range=price_range,
                    description=f'{name}，舒适面料，多色可选',
                    stock=random.randint(100, 500)
                )
                clothing_items.append(clothing)
                self.stdout.write(f'创建服装商品 {clothing.name} 成功')
            
            # 衬衫
            shirt_names = ['商务正装衬衫', '休闲格子衬衫', '牛津纺衬衫', '法兰绒衬衫', '亚麻衬衫']
            for name in shirt_names:
                price = random.randint(150, 600)
                price_range = next((pr for pr in price_ranges if pr.min_price <= price <= pr.max_price), price_ranges[1])
                clothing = Clothing.objects.create(
                    name=name,
                    clothing_type=next(ct for ct in clothing_types if ct.name == '衬衫'),
                    price=price,
                    price_range=price_range,
                    description=f'{name}，精选面料，剪裁合身',
                    stock=random.randint(100, 500)
                )
                clothing_items.append(clothing)
                self.stdout.write(f'创建服装商品 {clothing.name} 成功')
            
            # 裤子
            pants_names = ['修身牛仔裤', '直筒休闲裤', '运动裤', '工装裤', '西裤']
            for name in pants_names:
                price = random.randint(120, 500)
                price_range = next((pr for pr in price_ranges if pr.min_price <= price <= pr.max_price), price_ranges[1])
                clothing = Clothing.objects.create(
                    name=name,
                    clothing_type=next(ct for ct in clothing_types if ct.name == '裤子'),
                    price=price,
                    price_range=price_range,
                    description=f'{name}，舒适面料，穿着自如',
                    stock=random.randint(100, 500)
                )
                clothing_items.append(clothing)
                self.stdout.write(f'创建服装商品 {clothing.name} 成功')
            
            # 外套
            coat_names = ['羽绒服', '风衣', '夹克', '棉衣', '大衣']
            for name in coat_names:
                price = random.randint(300, 1500)
                price_range = next((pr for pr in price_ranges if pr.min_price <= price <= pr.max_price), price_ranges[2])
                clothing = Clothing.objects.create(
                    name=name,
                    clothing_type=next(ct for ct in clothing_types if ct.name == '外套'),
                    price=price,
                    price_range=price_range,
                    description=f'{name}，保暖舒适，设计时尚',
                    stock=random.randint(100, 500)
                )
                clothing_items.append(clothing)
                self.stdout.write(f'创建服装商品 {clothing.name} 成功')
            
            # 裙装
            dress_names = ['连衣裙', 'A字裙', '半身裙', '褶皱裙', '包臀裙']
            for name in dress_names:
                price = random.randint(200, 800)
                price_range = next((pr for pr in price_ranges if pr.min_price <= price <= pr.max_price), price_ranges[2])
                clothing = Clothing.objects.create(
                    name=name,
                    clothing_type=next(ct for ct in clothing_types if ct.name == '裙装'),
                    price=price,
                    price_range=price_range,
                    description=f'{name}，优雅气质，展现女性魅力',
                    stock=random.randint(100, 500)
                )
                clothing_items.append(clothing)
                self.stdout.write(f'创建服装商品 {clothing.name} 成功')
            
            # 西装
            suit_names = ['商务西装', '休闲西装', '结婚西装', '职业套装', '燕尾服']
            for name in suit_names:
                price = random.randint(800, 3000)
                price_range = next((pr for pr in price_ranges if pr.min_price <= price <= pr.max_price), price_ranges[3])
                clothing = Clothing.objects.create(
                    name=name,
                    clothing_type=next(ct for ct in clothing_types if ct.name == '西装'),
                    price=price,
                    price_range=price_range,
                    description=f'{name}，高级面料，精细做工',
                    stock=random.randint(50, 300)
                )
                clothing_items.append(clothing)
                self.stdout.write(f'创建服装商品 {clothing.name} 成功')
            
            # 补充所有商品数据
            clothing_items.extend(list(Clothing.objects.all()))
            
            # 创建销售订单和订单条目
            if SalesOrder.objects.count() < 100:  # 限制订单数量
                today = timezone.now()
                
                # 确保至少有30天的历史数据，用于预测
                for day_back in range(60, 0, -1):  # 生成最近60天的历史数据
                    order_date = today - datetime.timedelta(days=day_back)
                    
                    # 每天生成1-5个订单
                    daily_orders = random.randint(1, 5)
                    
                    for _ in range(daily_orders):
                        # 随机选择用户和地区
                        user = random.choice(test_users)
                        region = random.choice(regions)
                        
                        # 创建随机订单号
                        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                        
                        # 随机选择1-5件商品
                        order_items_count = random.randint(1, 5)
                        selected_items = random.sample(clothing_items, order_items_count)
                        
                        # 计算订单总额
                        total_amount = 0
                        
                        # 创建订单
                        order = SalesOrder.objects.create(
                            order_number=order_number,
                            user=user,
                            region=region,
                            total_amount=0,  # 临时值，稍后更新
                            order_date=order_date
                        )
                        
                        # 创建订单条目
                        for item in selected_items:
                            quantity = random.randint(1, 3)
                            price = item.price
                            item_total = price * quantity
                            total_amount += item_total
                            
                            OrderItem.objects.create(
                                order=order,
                                clothing=item,
                                quantity=quantity,
                                price=price
                            )
                        
                        # 更新订单总额
                        order.total_amount = total_amount
                        order.save()
                        
                        self.stdout.write(f'创建订单 {order.order_number} 成功，总额: ¥{total_amount}，日期: {order_date.strftime("%Y-%m-%d")}')
                        
                        # 有70%概率添加评价
                        if random.random() < 0.7:
                            for item in selected_items:
                                # 有80%概率是好评(4-5星)，20%概率是差评(1-3星)
                                if random.random() < 0.8:
                                    rating_value = random.randint(4, 5)
                                    category = random.choice(rating_categories[:7])  # 好评类别
                                else:
                                    rating_value = random.randint(1, 3)
                                    category = random.choice(rating_categories[7:])  # 差评类别
                                
                                Rating.objects.create(
                                    user=user,
                                    clothing=item,
                                    rating=rating_value,
                                    comment=f"用户{user.username}对{item.name}的评价",
                                    category=category,
                                    created_at=order_date + datetime.timedelta(days=random.randint(3, 15))
                                )
                                
                                self.stdout.write(f'为商品 {item.name} 创建{rating_value}星评价')
            
            self.stdout.write(self.style.SUCCESS('所有演示数据生成成功!'))
        else:
            self.stdout.write('服装商品数据已存在，跳过创建') 