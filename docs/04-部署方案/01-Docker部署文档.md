# Docker 部署文档

## 一、部署概述

### 1.1 部署架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         负载均衡器 (Nginx)                       │
└─────────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐       ┌───────────────────┐
│  Vue.js 前端  │       │  Django API 服务   │
│   (静态资源)   │       │   (Gunicorn)      │
└───────────────┘       └───────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────────┐       ┌───────────────┐
│  MySQL 数据库 │       │   Redis 服务器    │       │ Celery Worker │
└───────────────┘       └───────────────────┘       └───────────────┘
```

### 1.2 基础设施要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核以上 |
| 内存 | 4 GB | 8 GB 以上 |
| 存储 | 50 GB | 100 GB SSD |
| 带宽 | 5 Mbps | 10 Mbps 以上 |

---

## 二、环境准备

### 2.1 安装 Docker

```bash
# Ubuntu 系统
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
```

### 2.2 安装 Docker Compose

```bash
# Docker Compose v2
sudo mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 验证安装
docker compose version
```

### 2.3 验证安装

```bash
# 检查 Docker 版本
docker --version
docker-compose --version

# 运行测试容器
docker run hello-world
```

---

## 三、项目配置

### 3.1 目录结构

```
loadtest/
├── docker/
│   ├── nginx/
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── Dockerfile.prod
│   └── frontend/
│       ├── Dockerfile
│       └── Dockerfile.prod
├── docker-compose.yml
├── .env.example
├── .env
├── requirements.txt
└── frontend/
    └── package.json
```

### 3.2 环境变量配置

```bash
# .env.example

# ============ 数据库配置 ============
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=loadtest
MYSQL_USER=loadtest
MYSQL_PASSWORD=your_secure_password

# ============ Redis 配置 ============
REDIS_PASSWORD=your_redis_password

# ============ Django 配置 ============
SECRET_KEY=your-very-long-secret-key-at-least-50-characters
DEBUG=0
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,your-domain.com

# ============ JWT 配置 ============
JWT_SECRET_KEY=your-jwt-secret-key-at-least-32-characters
JWT_EXPIRATION_HOURS=24

# ============ 文件上传 ============
MAX_UPLOAD_SIZE=100
UPLOAD_PATH=./uploads

# ============ Celery 配置 ============
CELERY_BROKER_URL=redis://:your_redis_password@redis:6379/0
CELERY_RESULT_BACKEND=redis://:your_redis_password@redis:6379/1

# ============ CORS 配置 ============
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:80,https://your-domain.com

# ============ 邮件配置 (可选) ============
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 3.3 创建 .env 文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
nano .env
```

---

## 四、Docker Compose 配置

### 4.1 docker-compose.yml

```yaml
version: '3.8'

services:
  # MySQL 数据库
  db:
    image: mysql:8.0
    container_name: loadtest-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_CHARSET: utf8mb4
      MYSQL_COLLATION: utf8mb4_unicode_ci
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/conf.d:/etc/mysql/conf.d:ro
    ports:
      - "3306:3306"
    networks:
      - loadtest-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存和消息队列
  redis:
    image: redis:7-alpine
    container_name: loadtest-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - loadtest-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Django API 服务
  backend:
    build:
      context: .
      dockerfile: docker/backend/Dockerfile
    container_name: loadtest-backend
    restart: unless-stopped
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - MYSQL_HOST=db
      - MYSQL_PORT=3306
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_EXPIRATION_HOURS=${JWT_EXPIRATION_HOURS}
    volumes:
      - ./scenarios:/app/scenarios
      - ./reports:/app/reports
      - ./datasources:/app/datasources
      - ./logs:/app/logs
      - ./media:/app/media
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - loadtest-network

  # Celery Worker
  worker:
    build:
      context: .
      dockerfile: docker/backend/Dockerfile
    container_name: loadtest-worker
    restart: unless-stopped
    command: celery -A project worker -l info
    environment:
      - MYSQL_HOST=db
      - MYSQL_PORT=3306
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    volumes:
      - ./scenarios:/app/scenarios
      - ./reports:/app/reports
      - ./datasources:/app/datasources
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - loadtest-network

  # Celery Beat (定时任务)
  beat:
    build:
      context: .
      dockerfile: docker/backend/Dockerfile
    container_name: loadtest-beat
    restart: unless-stopped
    command: celery -A project beat -l info
    environment:
      - MYSQL_HOST=db
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - loadtest-network

  # Nginx 反向代理
  nginx:
    build:
      context: docker/nginx
      dockerfile: Dockerfile
    container_name: loadtest-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - loadtest-network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  mysql_data:
    driver: local
  redis_data:
    driver: local

networks:
  loadtest-network:
    driver: bridge
```

---

## 五、Dockerfile 配置

### 5.1 后端 Dockerfile

```dockerfile
# docker/backend/Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    libpq-dev \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建必要目录
RUN mkdir -p /app/logs /app/scenarios /app/reports /app/datasources /app/media

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "project.wsgi:application"]
```

### 5.2 前端 Dockerfile

```dockerfile
# docker/frontend/Dockerfile
# 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制代码并构建
COPY . .
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 5.3 Nginx 配置

```nginx
# docker/nginx/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        
        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 重试
        proxy_next_upstream error timeout http_500 http_502 http_503;
        proxy_next_upstream_tries 3;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # 媒体文件
    location /media/ {
        alias /app/media/;
    }

    # 健康检查
    location /health/ {
        proxy_pass http://backend:8000;
    }

    # Vue Router SPA 支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

# HTTPS 配置 (可选)
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=63072000" always;

    # 其他配置同上...
}
```

---

## 六、部署步骤

### 6.1 开发环境部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd loadtest

# 2. 复制环境变量文件
cp .env.example .env
# 编辑 .env 文件配置数据库密码等

# 3. 构建并启动服务
docker compose build
docker compose up -d

# 4. 查看服务状态
docker compose ps

# 5. 查看日志
docker compose logs -f

# 6. 执行数据库迁移
docker compose exec backend python manage.py migrate

# 7. 创建超级用户
docker compose exec backend python manage.py createsuperuser

# 8. 访问应用
# 浏览器打开 http://localhost
```

### 6.2 生产环境部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新依赖
docker compose -f docker-compose.prod.yml build --no-cache

# 3. 执行数据库迁移
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 4. 收集静态文件
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# 5. 重启服务
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# 6. 检查服务状态
docker compose -f docker-compose.prod.yml ps

# 7. 查看日志
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

### 6.3 使用 Makefile

```makefile
# Makefile

.PHONY: help build up down logs migrate restart

help:
	@echo "可用命令:"
	@echo "  make up        - 启动所有服务"
	@echo "  make down      - 停止所有服务"
	@echo "  make logs      - 查看日志"
	@echo "  make migrate   - 执行数据库迁移"
	@echo "  make restart   - 重启所有服务"
	@echo "  make backup    - 备份数据库"
	@echo "  make restore   - 恢复数据库"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend python manage.py migrate

restart:
	docker compose down
	docker compose up -d

backup:
	docker compose exec db mysqldump -u root -p${MYSQL_ROOT_PASSWORD} loadtest > backup_$$(date +%Y%m%d_%H%M%S).sql

restore:
	@read -p "输入备份文件路径: " file; \
	docker compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} loadtest < $$file
```

---

## 七、服务管理

### 7.1 常用命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f backend

# 查看实时日志
docker compose logs -f --tail=100

# 进入容器
docker compose exec backend bash

# 查看资源使用
docker stats

# 查看网络
docker network ls
docker network inspect loadtest_loadtest-network

# 查看磁盘使用
docker system df
```

### 7.2 扩容命令

```bash
# 扩容 backend 服务到 8 个 worker
docker compose up -d --scale backend=8

# 扩容 worker 到 4 个
docker compose up -d --scale worker=4
```

---

## 八、监控与日志

### 8.1 日志配置

```python
# project/logging.py
import logging
from django.conf import settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 8.2 健康检查

```python
# project/health.py
from django.http import JsonResponse
from django.db import connection
from redis import Redis


def health_check(request):
    status = {
        'status': 'healthy',
        'components': {}
    }
    
    # 检查数据库
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        status['components']['database'] = 'healthy'
    except Exception as e:
        status['components']['database'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    # 检查 Redis
    try:
        redis = Redis(host='redis', port=6379, password='your_password')
        redis.ping()
        status['components']['redis'] = 'healthy'
    except Exception as e:
        status['components']['redis'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    return JsonResponse(status)
```

---

## 九、备份与恢复

### 9.1 自动备份脚本

```bash
#!/bin/bash
# scripts/backup.sh

# 备份目录
BACKUP_DIR="/backup/loadtest"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 备份数据库
echo "备份数据库..."
docker compose exec -T db mysqldump -u root -p${MYSQL_ROOT_PASSWORD} \
    --single-transaction --routines --triggers \
    loadtest | gzip > ${BACKUP_DIR}/loadtest_db_${DATE}.sql.gz

# 备份上传文件
echo "备份上传文件..."
tar -czf ${BACKUP_DIR}/loadtest_uploads_${DATE}.tar.gz ./uploads

# 清理旧备份 (保留 7 天)
echo "清理旧备份..."
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete

# 同步到远程存储 (可选)
# aws s3 sync ${BACKUP_DIR} s3://your-backup-bucket/loadtest/

echo "备份完成: ${DATE}"
```

### 9.2 添加定时任务

```bash
# 编辑 crontab
crontab -e

# 添加定时任务 (每天凌晨 3 点执行)
0 3 * * * /app/loadtest/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### 9.3 数据恢复

```bash
# 从备份文件恢复数据库
docker compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} loadtest < backup_file.sql

# 从压缩文件恢复
gunzip -c backup_file.sql.gz | docker compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} loadtest

# 恢复上传文件
tar -xzf backup_file.tar.gz -C /
```

---

## 十、故障排查

### 10.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 502 Bad Gateway | backend 服务未启动 | 检查 backend 容器状态和日志 |
| 数据库连接失败 | 数据库未就绪 | 等待数据库健康检查通过 |
| 前端页面 404 | nginx 配置问题 | 检查 nginx 配置和前端构建产物 |
| 文件上传失败 | 权限问题 | 检查挂载目录权限 |
| WebSocket 连接失败 | 反向代理配置 | 检查 nginx WebSocket 配置 |

### 10.2 调试命令

```bash
# 检查容器状态
docker compose ps -a

# 查看容器资源使用
docker stats --no-stream

# 进入容器调试
docker compose exec backend sh

# 检查网络
docker network inspect loadtest_loadtest-network

# 检查磁盘空间
df -h

# 检查 Docker 日志
docker system events

# 清理未使用资源
docker system prune -a
```

---

## 十一、性能优化

### 11.1 Docker 优化

```yaml
# docker-compose.prod.yml 中添加
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
```

### 11.2 Gunicorn 优化

```bash
# 启动命令优化
gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    project.wsgi:application
```

### 11.3 MySQL 优化

```ini
# mysql/conf.d/optimization.cnf
[mysqld]
# 连接数
max_connections = 200

# 缓存
innodb_buffer_pool_size = 1G
innodb_buffer_pool_instances = 4

# 日志
innodb_log_file_size = 256M
innodb_log_buffer_size = 64M

# 查询优化
max_heap_table_size = 256M
tmp_table_size = 256M
```

---

## 十二、版本更新

### 12.1 更新流程

```bash
# 1. 备份当前数据
./scripts/backup.sh

# 2. 拉取最新代码
git pull origin main

# 3. 更新前端依赖并构建
cd frontend
npm install
npm run build
cd ..

# 4. 更新后端依赖
docker compose exec backend pip install -r requirements.txt

# 5. 执行数据库迁移
docker compose exec backend python manage.py migrate

# 6. 重启服务
docker compose down
docker compose up -d

# 7. 验证更新
curl http://localhost/api/health/
```

### 12.2 回滚流程

```bash
# 1. 查看历史版本
git log --oneline -10

# 2. 回滚代码
git checkout <previous-commit-hash>

# 3. 回滚数据库
docker compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} loadtest < backup_file.sql

# 4. 重启服务
docker compose down
docker compose up -d
```
