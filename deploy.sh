#!/bin/bash

# 部署脚本
set -e

echo "开始部署压测管理平台..."

# 检查是否安装了必要的工具
if ! [ -x "$(command -v docker)" ]; then
  echo "错误: docker 未安装" >&2
  exit 1
fi

if ! [ -x "$(command -v docker-compose)" ]; then
  echo "错误: docker-compose 未安装" >&2
  exit 1
fi

# 获取当前分支名作为环境标识
ENVIRONMENT=${1:-prod}

echo "部署环境: $ENVIRONMENT"

if [ "$ENVIRONMENT" = "dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    echo "使用开发环境配置..."
else
    COMPOSE_FILE="docker-compose.yml"
    echo "使用生产环境配置..."
fi

echo "拉取最新代码..."
git pull origin main

echo "构建镜像..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml build
else
    docker-compose -f docker-compose.yml build
fi

echo "启动服务..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml up -d
else
    docker-compose -f docker-compose.yml up -d
fi

echo "等待服务启动..."
sleep 10

if [ "$ENVIRONMENT" != "dev" ]; then
    echo "执行数据库迁移..."
    docker-compose -f docker-compose.yml exec backend python manage.py migrate --noinput
    
    echo "收集静态文件..."
    docker-compose -f docker-compose.yml exec backend python manage.py collectstatic --noinput
fi

echo "部署完成!"
echo "访问地址:"
if [ "$ENVIRONMENT" = "dev" ]; then
    echo "  前端: http://localhost:3000"
    echo "  后端: http://localhost:8000"
else
    echo "  前端: http://localhost"
    echo "  后端: http://localhost:8000"
fi

echo ""
echo "查看日志:"
echo "  docker-compose -f $COMPOSE_FILE logs -f"