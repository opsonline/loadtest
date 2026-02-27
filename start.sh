#!/bin/bash
# 启动压测系统项目

echo "正在启动压测管理系统..."
echo "=========================="

# 检查并启动后端
echo "1. 检查后端..."
cd backend

# 运行数据库迁移
echo "运行数据库迁移..."
python3 manage.py migrate

# 创建默认管理员用户（如果不存在）
echo "检查管理员用户..."
python3 manage.py shell <<EOF
from apps.users.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✓ 已创建管理员用户 (admin / admin123)')
else:
    print('✓ 管理员用户已存在 (admin / admin123)')
EOF

echo "✓ 后端准备完成"
echo ""
echo "2. 后端服务已启动在 http://localhost:8000"
echo "3. 前端需要单独启动，请在新终端运行："
echo ""
echo "   cd frontend && npm install && npm run dev"
echo ""
echo "后端服务日志："
echo "=========================="

# 启动后端服务
python3 manage.py runserver 0.0.0.0:8000