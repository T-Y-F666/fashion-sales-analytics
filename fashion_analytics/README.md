# 服装销售分析系统

这是一个基于Django + Vue的服装销售数据分析系统，用于分析服装销售数据并提供可视化展示。

## 后端环境设置

1. 确保已安装Python 3.8+和MySQL

2. 创建并激活虚拟环境：
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

4. 数据库配置：
   - 在MySQL中创建数据库：
     ```sql
     CREATE DATABASE fashion_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```
   - 或者修改`fashion_analytics/settings.py`中的数据库配置

5. 执行数据库迁移：
   ```
   python manage.py migrate
   ```

6. 生成测试数据：
   ```
   python manage.py generate_demo_data
   ```

7. 启动开发服务器：
   ```
   python manage.py runserver
   ```

## 前端环境设置

1. 确保已安装Node.js和npm

2. 进入前端项目目录：
   ```
   cd ../fashion-analytics-frontend
   ```

3. 安装依赖：
   ```
   npm install
   ```

4. 启动开发服务器：
   ```
   npm run dev
   ```

## 系统账号

使用generate_demo_data命令创建的测试账号：

- 管理员账号：
  - 用户名：admin
  - 密码：admin123

- 测试用户账号：
  - 用户名：user1 到 user10
  - 密码：password123

## 数据结构

系统包含以下主要数据模型：

1. 地区(Region)：销售区域划分
2. 服装类型(ClothingType)：如T恤、衬衫、裤子等
3. 价格区间(PriceRange)：按价格分类
4. 评价类别(RatingCategory)：用户评价分类
5. 服装商品(Clothing)：销售的具体服装
6. 销售订单(SalesOrder)：用户订单
7. 订单条目(OrderItem)：订单中的商品明细
8. 商品评价(Rating)：用户对商品的评价

## 功能特点

1. 用户认证：注册、登录、登出
2. 数据分析：
   - 地区销售数据分析
   - 服装类型销售占比分析
   - 价格区间销量分析
   - 服装评价分析
3. 销售预测：
   - 销量预测
   - 价格预测 