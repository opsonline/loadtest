# 压测管理平台

基于 Web 的压测管理系统，支持 HAR 文件导入、场景管理、压测执行、报告分析等功能。

## 技术栈

### 后端
- **Django 4.2** - Web 框架
- **Django REST Framework** - API 框架
- **Celery** - 异步任务队列
- **Locust** - 压测引擎
- **SQLite** - 开发数据库

### 前端
- **Vue 3** - 前端框架
- **Element Plus** - UI 组件库
- **Vite** - 构建工具
- **Pinia** - 状态管理
- **ECharts** - 图表库

## 项目结构

```
.
├── backend/              # Django 后端
│   ├── apps/            # 应用模块
│   │   ├── users/       # 用户管理
│   │   ├── scenarios/   # 场景管理
│   │   ├── reports/     # 报告管理
│   │   ├── environments/# 环境变量
│   │   ├── datasources/ # 数据源
│   │   └── api_tests/   # 接口测试
│   ├── config/          # Django 配置
│   ├── manage.py        # Django 管理脚本
│   ├── requirements.txt # Python 依赖
│   └── venv/            # Python 虚拟环境
│
├── frontend/            # Vue 前端
│   ├── src/            # 源代码
│   │   ├── api/        # API 接口
│   │   ├── components/ # 组件
│   │   ├── router/     # 路由
│   │   ├── store/      # 状态管理
│   │   ├── views/      # 页面
│   │   └── utils/      # 工具函数
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── docs/               # 项目文档
```

## 快速开始

### 后端启动

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

后端服务默认运行在 http://localhost:8000

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务默认运行在 http://localhost:3000

## 功能模块

### 已规划功能

1. **用户认证** - JWT Token 认证、用户注册/登录
2. **场景管理** - 创建/编辑/删除压测场景
3. **HAR 导入** - 上传 HAR 文件自动生成场景
4. **压测执行** - 基于 Locust 的压测引擎
5. **报告管理** - 查看/对比/导出压测报告
6. **环境变量** - 多环境配置管理
7. **数据源** - CSV/JSON/数据库等多种数据源
8. **接口测试** - 类似 Postman 的接口测试功能

## API 文档

API 接口遵循 RESTful 规范，基础路径：`/api/v1/`

### 主要接口

- `POST /api/v1/users/login/` - 用户登录
- `POST /api/v1/users/register/` - 用户注册
- `GET /api/v1/users/profile/` - 获取用户信息
- `GET /api/v1/scenarios/` - 场景列表
- `POST /api/v1/scenarios/` - 创建场景
- `GET /api/v1/reports/` - 报告列表
- `GET /api/v1/environments/` - 环境列表
- `GET /api/v1/datasources/` - 数据源列表
- `GET /api/v1/api-tests/` - 接口测试

## 开发规范

### Git 提交规范

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建/工具
```

### API 响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "meta": {
    "pagination": {}
  }
}
```

## 下一步开发计划

1. 完成后端 API 实现
2. 实现 HAR 解析器
3. 集成 Locust 压测引擎
4. 完善前端页面
5. 实现实时压测监控
6. 添加报告图表展示

## 参考文档

- [Django 文档](https://docs.djangoproject.com)
- [Django REST Framework](https://www.django-rest-framework.org)
- [Vue.js 文档](https://vuejs.org)
- [Element Plus](https://element-plus.org)
- [Locust 文档](https://docs.locust.io)

## License

MIT
