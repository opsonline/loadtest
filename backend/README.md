# 压测系统后端配置

## 环境变量配置

创建 `.env` 文件：

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
JWT_SECRET_KEY=your-jwt-secret-key
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 启动步骤

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 执行迁移：
```bash
python manage.py migrate
```

3. 创建超级用户：
```bash
python manage.py createsuperuser
```

4. 启动服务：
```bash
python manage.py runserver
```

5. 启动 Celery（可选）：
```bash
celery -A config worker -l info
celery -A config beat -l info
```
