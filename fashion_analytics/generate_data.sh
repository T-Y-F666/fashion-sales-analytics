#!/bin/bash
echo "开始初始化数据..."

echo "执行数据库迁移..."
python manage.py migrate

echo "生成示例数据..."
python manage.py generate_demo_data

echo "初始化完成!"
echo "您可以使用以下用户登录:"
echo "管理员: admin/admin123"
echo "测试用户: user1到user10/password123"
echo ""
echo "按Enter键退出..."
read 