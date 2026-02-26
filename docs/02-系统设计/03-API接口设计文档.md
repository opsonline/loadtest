# API 接口设计文档

## 一、接口规范

### 1.1 RESTful 设计原则

| 原则 | 说明 |
|------|------|
| 资源命名 | 使用名词复数形式，如 `/api/users`、`/api/scenarios` |
| HTTP 方法 | GET（查询）、POST（创建）、PUT（更新）、DELETE（删除） |
| 状态码 | 200 成功、201 创建成功、400 参数错误、401 未认证、404 不存在、500 服务器错误 |
| 版本控制 | URL 版本前缀，如 `/api/v1/` |

### 1.2 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 业务数据
  }
}
```

### 1.3 错误响应格式

```json
{
  "code": 40001,
  "message": "参数验证失败",
  "data": null
}
```

---

## 二、用户认证接口

### 2.1 用户注册

**接口**: `POST /api/v1/auth/register/`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名，4-20 位 |
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码，8-32 位 |
| phone | string | 否 | 手机号 |

**请求示例**:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Password123!",
  "phone": "13800138000"
}
```

**响应示例**:

```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user": {
      "id": "uuid",
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

### 2.2 用户登录

**接口**: `POST /api/v1/auth/login/`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名或邮箱 |
| password | string | 是 | 密码 |

**响应示例**:

```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "Bearer",
      "expires_in": 86400
    },
    "user": {
      "id": "uuid",
      "username": "testuser",
      "email": "test@example.com",
      "role": "developer"
    }
  }
}
```

### 2.3 获取当前用户

**接口**: `GET /api/v1/auth/me/`

**请求头**: `Authorization: Bearer <token>`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "avatar": "https://example.com/avatar.png",
    "role": "developer",
    "is_active": true,
    "date_joined": "2026-02-12T00:00:00Z"
  }
}
```

### 2.4 刷新 Token

**接口**: `POST /api/v1/auth/refresh/`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| refresh_token | string | 是 | 刷新 Token |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "new_access_token",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

---

## 三、场景管理接口

### 3.1 获取场景列表

**接口**: `GET /api/v1/scenarios/`

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| project_id | uuid | 否 | 项目 ID 筛选 |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20 |
| search | string | 模糊搜索名称 |
| ordering | string | 排序字段，如 `-created_at` |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "登录接口压测",
        "description": "测试登录接口性能",
        "target_host": "https://api.example.com",
        "request_count": 5,
        "created_at": "2026-02-12T00:00:00Z",
        "updated_at": "2026-02-12T00:00:00Z"
      }
    ],
    "meta": {
      "pagination": {
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
      }
    }
  }
}
```

### 3.2 获取场景详情

**接口**: `GET /api/v1/scenarios/{id}/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "登录接口压测",
    "description": "测试登录接口性能",
    "target_host": "https://api.example.com",
    "environment": {
      "id": "uuid",
      "name": "测试环境"
    },
    "config": {
      "user_count": 100,
      "spawn_rate": 10
    },
    "requests": [
      {
        "id": "uuid",
        "name": "登录",
        "method": "POST",
        "url": "/api/auth/login",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": "{\"username\":\"${username}\",\"password\":\"${password}\"}",
        "body_type": "json",
        "weight": 1,
        "think_time": 1.5,
        "timeout": 30,
        "order": 0,
        "is_enabled": true
      }
    ],
    "created_at": "2026-02-12T00:00:00Z",
    "updated_at": "2026-02-12T00:00:00Z"
  }
}
```

### 3.3 创建场景

**接口**: `POST /api/v1/scenarios/`

**请求参数**:

```json
{
  "name": "新场景",
  "description": "场景描述",
  "target_host": "https://api.example.com",
  "environment_id": "uuid",
  "config": {
    "user_count": 100,
    "spawn_rate": 10
  },
  "requests": [
    {
      "name": "请求1",
      "method": "GET",
      "url": "/api/users",
      "headers": {},
      "body": null,
      "body_type": "none",
      "weight": 1,
      "think_time": 0,
      "timeout": 30,
      "order": 0
    }
  ]
}
```

### 3.4 更新场景

**接口**: `PUT /api/v1/scenarios/{id}/`

**请求参数**: 同创建接口，只提交需要更新的字段

### 3.5 删除场景

**接口**: `DELETE /api/v1/scenarios/{id}/`

**响应示例**:

```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

### 3.6 复制场景

**接口**: `POST /api/v1/scenarios/{id}/duplicate/`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 否 | 新场景名称，默认"原名称 (副本)" |

**响应示例**:

```json
{
  "code": 0,
  "message": "复制成功",
  "data": {
    "id": "new_uuid",
    "name": "登录接口压测 (副本)"
  }
}
```

### 3.7 导入 HAR 文件

**接口**: `POST /api/v1/scenarios/{id}/import-har/`

**请求方式**: `multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | HAR 文件 |
| resource_types | string | 否 | 资源类型过滤，逗号分隔 |
| replace_host | boolean | 否 | 是否替换 Host |
| target_host | string | 否 | 目标 Host |

**响应示例**:

```json
{
  "code": 0,
  "message": "导入成功",
  "data": {
    "scenario_id": "uuid",
    "requests_imported": 25,
    "requests_filtered": 5
  }
}
```

### 3.8 批量更新请求

**接口**: `PUT /api/v1/scenarios/{id}/requests/bulk/`

**请求参数**:

```json
{
  "requests": [
    {
      "id": "uuid",
      "name": "更新后的请求",
      "method": "GET",
      "url": "/api/updated",
      "weight": 2,
      "think_time": 1.0
    }
  ]
}
```

---

## 四、压测执行接口

### 4.1 启动压测

**接口**: `POST /api/v1/runs/start/`

**请求参数**:

```json
{
  "scenario_id": "uuid",
  "config": {
    "user_count": 100,
    "spawn_rate": 10,
    "duration": 300,
    "host": "https://api.example.com"
  },
  "environment_id": "uuid"
}
```

**响应示例**:

```json
{
  "code": 0,
  "message": "压测已启动",
  "data": {
    "run_id": "uuid",
    "status": "running",
    "websocket_url": "/api/ws/runs/{run_id}/stats/"
  }
}
```

### 4.2 停止压测

**接口**: `POST /api/v1/runs/{id}/stop/`

**响应示例**:

```json
{
  "code": 0,
  "message": "压测已停止",
  "data": {
    "run_id": "uuid",
    "status": "stopped",
    "duration": 125.5,
    "total_requests": 50000
  }
}
```

### 4.3 获取运行状态

**接口**: `GET /api/v1/runs/{id}/status/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "run_id": "uuid",
    "scenario_id": "uuid",
    "status": "running",
    "config": {
      "user_count": 100,
      "spawn_rate": 10,
      "duration": 300
    },
    "current_user_count": 75,
    "start_time": "2026-02-12T10:00:00Z",
    "elapsed_time": 60.5
  }
}
```

### 4.4 获取实时统计

**接口**: `GET /api/v1/runs/{id}/stats/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "timestamp": "2026-02-12T10:01:00Z",
    "user_count": 75,
    "total_requests": 25000,
    "total_failures": 15,
    "avg_response_time": 125.5,
    "min_response_time": 10.2,
    "max_response_time": 2500.0,
    "p50_response_time": 80.0,
    "p90_response_time": 200.0,
    "p99_response_time": 800.0,
    "requests_per_second": 416.7,
    "failures_per_second": 0.25,
    "error_rate": 0.06
  }
}
```

---

## 五、报告管理接口

### 5.1 获取报告列表

**接口**: `GET /api/v1/reports/`

**查询参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| project_id | uuid | 项目筛选 |
| scenario_id | uuid | 场景筛选 |
| status | string | 状态筛选 |
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |
| page | int | 页码 |
| page_size | int | 每页数量 |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "登录接口压测 - 2026-02-12",
        "scenario_name": "登录接口压测",
        "status": "completed",
        "duration": 300.5,
        "total_requests": 150000,
        "avg_response_time": 125.5,
        "error_rate": 0.02,
        "rps": 500.0,
        "created_at": "2026-02-12T10:00:00Z"
      }
    ],
    "meta": {
      "pagination": {
        "total": 50,
        "page": 1,
        "page_size": 20,
        "total_pages": 3
      }
    }
  }
}
```

### 5.2 获取报告详情

**接口**: `GET /api/v1/reports/{id}/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "登录接口压测 - 2026-02-12",
    "scenario_id": "uuid",
    "scenario_name": "登录接口压测",
    "status": "completed",
    "config": {
      "user_count": 100,
      "spawn_rate": 10,
      "duration": 300
    },
    "stats": {
      "total_requests": 150000,
      "total_failures": 30,
      "success_rate": 99.98,
      "avg_response_time": 125.5,
      "min_response_time": 10.2,
      "max_response_time": 2500.0,
      "p50_response_time": 80.0,
      "p90_response_time": 200.0,
      "p95_response_time": 350.0,
      "p99_response_time": 800.0,
      "requests_per_second": 500.0,
      "error_types": {
        "ConnectionError": 15,
        "Timeout": 10,
        "AssertionError": 5
      }
    },
    "start_time": "2026-02-12T10:00:00Z",
    "end_time": "2026-02-12T10:05:00Z",
    "duration": 300.0,
    "created_at": "2026-02-12T10:00:00Z"
  }
}
```

### 5.3 获取图表数据

**接口**: `GET /api/v1/reports/{id}/charts/`

**查询参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| metrics | string | 指标，多个用逗号分隔 |
| interval | int | 数据聚合间隔（秒），默认 1 |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "rps": {
      "title": "RPS",
      "data": [
        {"timestamp": "2026-02-12T10:00:00Z", "value": 100},
        {"timestamp": "2026-02-12T10:00:01Z", "value": 150}
      ]
    },
    "response_time": {
      "title": "响应时间",
      "data": [
        {"timestamp": "2026-02-12T10:00:00Z", "p50": 80, "p90": 200, "p99": 500}
      ]
    },
    "users": {
      "title": "并发用户数",
      "data": [
        {"timestamp": "2026-02-12T10:00:00Z", "value": 50}
      ]
    },
    "errors": {
      "title": "错误数",
      "data": [
        {"timestamp": "2026-02-12T10:00:00Z", "value": 2}
      ]
    }
  }
}
```

### 5.4 获取请求级别统计

**接口**: `GET /api/v1/reports/{id}/requests/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "登录",
        "method": "POST",
        "url": "/api/auth/login",
        "total_requests": 50000,
        "failures": 10,
        "avg_response_time": 150.0,
        "p50": 100.0,
        "p90": 300.0,
        "rps": 166.7,
        "error_rate": 0.02
      },
      {
        "id": "uuid",
        "name": "获取用户信息",
        "method": "GET",
        "url": "/api/users/me",
        "total_requests": 100000,
        "failures": 20,
        "avg_response_time": 80.0,
        "p50": 50.0,
        "p90": 150.0,
        "rps": 333.3,
        "error_rate": 0.02
      }
    ]
  }
}
```

### 5.5 对比报告

**接口**: `POST /api/v1/reports/compare/`

**请求参数**:

```json
{
  "report_ids": ["uuid1", "uuid2"]
}
```

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reports": [
      {
        "id": "uuid1",
        "name": "压测报告1",
        "total_requests": 150000,
        "avg_response_time": 125.5,
        "error_rate": 0.02
      },
      {
        "id": "uuid2",
        "name": "压测报告2",
        "total_requests": 200000,
        "avg_response_time": 110.2,
        "error_rate": 0.01
      }
    ],
    "comparison": {
      "total_requests": {"increase": 33.3, "unit": "%"},
      "avg_response_time": {"decrease": 12.2, "unit": "%"},
      "error_rate": {"decrease": 50.0, "unit": "%"}
    },
    "charts": {
      // 对比图表数据
    }
  }
}
```

### 5.6 导出报告

**接口**: `GET /api/v1/reports/{id}/export/?format=json`

**查询参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| format | string | 格式：json、pdf |

**响应**: 文件下载

---

## 六、环境变量接口

### 6.1 获取环境列表

**接口**: `GET /api/v1/environments/`

**查询参数**: `project_id`（必填）

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "测试环境",
        "variables": {
          "BASE_URL": "https://api.test.example.com",
          "TOKEN": "***"
        },
        "is_default": true,
        "created_at": "2026-02-12T00:00:00Z"
      }
    ]
  }
}
```

### 6.2 创建环境

**接口**: `POST /api/v1/environments/`

**请求参数**:

```json
{
  "project_id": "uuid",
  "name": "生产环境",
  "variables": {
    "BASE_URL": "https://api.example.com",
    "API_KEY": "your-api-key",
    "DATABASE_HOST": "db.example.com"
  },
  "is_default": false
}
```

### 6.3 更新环境

**接口**: `PUT /api/v1/environments/{id}/`

**请求参数**: 同创建接口

### 6.4 删除环境

**接口**: `DELETE /api/v1/environments/{id}/`

### 6.5 设为默认

**接口**: `POST /api/v1/environments/{id}/set-default/`

---

## 七、数据源接口

### 7.1 获取数据源列表

**接口**: `GET /api/v1/datasources/`

**查询参数**: `project_id`（必填）

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "测试用户数据",
        "type": "csv",
        "status": "ready",
        "row_count": 1000,
        "created_at": "2026-02-12T00:00:00Z"
      }
    ]
  }
}
```

### 7.2 创建数据源

**接口**: `POST /api/v1/datasources/`

**请求方式**: `multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| project_id | uuid | 是 | 项目 ID |
| name | string | 是 | 数据源名称 |
| type | string | 是 | 类型 |
| file | File | 条件 | 文件 |
| config | JSON | 条件 | 连接配置 |
| script | string | 条件 | 生成脚本 |

**响应示例**:

```json
{
  "code": 0,
  "message": "创建成功",
  "data": {
    "id": "uuid",
    "name": "用户数据",
    "type": "csv",
    "status": "processing",
    "row_count": null
  }
}
```

### 7.3 获取数据预览

**接口**: `GET /api/v1/datasources/{id}/preview/`

**查询参数**: `limit`（默认 10）

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "columns": ["username", "password", "email"],
    "rows": [
      ["user1", "pass1", "user1@example.com"],
      ["user2", "pass2", "user2@example.com"]
    ],
    "total_rows": 1000
  }
}
```

### 7.4 测试连接

**接口**: `POST /api/v1/datasources/{id}/test/`

**响应示例**:

```json
{
  "code": 0,
  "message": "连接成功",
  "data": {
    "connected": true,
    "response_time": 15.5,
    "message": "成功连接到 MySQL 数据库"
  }
}
```

### 7.5 执行脚本生成

**接口**: `POST /api/v1/datasources/{id}/generate/`

**请求参数**:

```json
{
  "params": {
    "count": 100,
    "prefix": "test_"
  }
}
```

---

## 八、测试套件接口

### 8.1 获取测试套件列表

**接口**: `GET /api/v1/testsuites/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "登录模块测试",
        "request_count": 5,
        "last_run_at": "2026-02-12T10:00:00Z",
        "last_result": "passed",
        "created_at": "2026-02-12T00:00:00Z"
      }
    ]
  }
}
```

### 8.2 获取测试套件详情

**接口**: `GET /api/v1/testsuites/{id}/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "登录模块测试",
    "description": "测试登录相关接口",
    "environment": {
      "id": "uuid",
      "name": "测试环境"
    },
    "requests": [
      {
        "id": "uuid",
        "name": "登录",
        "method": "POST",
        "url": "/api/auth/login",
        "headers": {},
        "body": "{\"username\":\"${username}\",\"password\":\"${password}\"}",
        "body_type": "json",
        "order": 0,
        "is_enabled": true,
        "assertions": [
          {
            "id": "uuid",
            "assert_type": "status_code",
            "field": "",
            "operator": "eq",
            "expected_value": "200"
          },
          {
            "id": "uuid",
            "assert_type": "json_path",
            "field": "code",
            "operator": "eq",
            "expected_value": "0"
          }
        ]
      }
    ],
    "created_at": "2026-02-12T00:00:00Z"
  }
}
```

### 8.3 创建测试套件

**接口**: `POST /api/v1/testsuites/`

**请求参数**:

```json
{
  "project_id": "uuid",
  "name": "用户模块测试",
  "description": "测试用户相关接口",
  "environment_id": "uuid",
  "requests": [
    {
      "name": "获取用户信息",
      "method": "GET",
      "url": "/api/users/${user_id}",
      "headers": {
        "Authorization": "Bearer ${token}"
      },
      "body": null,
      "body_type": "none",
      "order": 0,
      "is_enabled": true,
      "assertions": [
        {
          "assert_type": "status_code",
          "field": "",
          "operator": "eq",
          "expected_value": "200"
        }
      ]
    }
  ]
}
```

### 8.4 执行测试套件

**接口**: `POST /api/v1/testsuites/{id}/run/`

**响应示例**:

```json
{
  "code": 0,
  "message": "测试执行中",
  "data": {
    "execution_id": "uuid",
    "status": "running"
  }
}
```

### 8.5 获取测试结果

**接口**: `GET /api/v1/testsuites/{id}/results/`

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "test_request": {
          "id": "uuid",
          "name": "登录"
        },
        "status": "passed",
        "response_status": 200,
        "response_time": 125.5,
        "assertions_passed": 2,
        "assertions_failed": 0,
        "executed_at": "2026-02-12T10:00:00Z"
      }
    ],
    "summary": {
      "total": 5,
      "passed": 4,
      "failed": 1,
      "errors": 0
    }
  }
}
```

---

## 九、WebSocket 接口

### 9.1 压测实时数据

**URL**: `ws://host/api/ws/runs/{run_id}/stats/`

**消息格式**:

```json
{
  "type": "stats",
  "data": {
    "timestamp": "2026-02-12T10:01:00Z",
    "user_count": 75,
    "total_requests": 25000,
    "total_failures": 15,
    "avg_response_time": 125.5,
    "requests_per_second": 416.7,
    "error_rate": 0.06
  }
}
```

### 9.2 控制命令

**客户端发送**:

```json
{
  "type": "control",
  "action": "stop"
}
```

**服务端响应**:

```json
{
  "type": "control",
  "status": "stopped"
}
```

### 9.3 心跳检测

**客户端发送**:

```json
{
  "type": "ping"
}
```

**服务端响应**:

```json
{
  "type": "pong"
}
```

---

## 十、错误码定义

### 10.1 通用错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 40000 | 参数错误 |
| 40001 | 参数验证失败 |
| 40100 | 未认证 |
| 40101 | Token 已过期 |
| 40102 | 无效的 Token |
| 40300 | 权限不足 |
| 40400 | 资源不存在 |
| 50000 | 服务器错误 |

### 10.2 业务错误码

| 错误码 | 模块 | 说明 |
|--------|------|------|
| 10001 | 场景 | 场景不存在 |
| 10002 | 场景 | 场景名称重复 |
| 10003 | 场景 | 请求不存在 |
| 10004 | 场景 | HAR 文件解析失败 |
| 20001 | 报告 | 报告不存在 |
| 20002 | 报告 | 报告生成中 |
| 30001 | 环境 | 环境不存在 |
| 30002 | 环境 | 默认环境设置失败 |
| 40001 | 数据源 | 连接失败 |
| 40002 | 数据源 | 数据源不存在 |
| 50001 | 测试 | 断言配置错误 |
| 50002 | 测试 | 测试执行超时 |
