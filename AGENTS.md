# AGENTS.md - Developer Guide for AI Agents

This document provides guidance for AI agents working on this load testing management platform.

## Project Overview

This is a load testing management platform with:
- **Backend**: Django 4.2 + Django REST Framework + Celery + Locust
- **Frontend**: Vue 3 + Element Plus + Vite + Pinia
- **Database**: SQLite (development)

## Build/Lint/Test Commands

### Backend (Django)

```bash
# Activate virtual environment
cd backend && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser
```

### Running Tests

```bash
# Run all tests
cd backend && python manage.py test

# Run all tests with pytest (recommended)
cd backend && pytest

# Run a specific test file
cd backend && pytest apps/users/tests/test_users.py

# Run a specific test class
cd backend && pytest apps/users/tests/test_users.py::UserLoginTests

# Run a specific test method
cd backend && pytest apps/users/tests/test_users.py::UserLoginTests::test_successful_login

# Run tests with markers (unit/integration/slow)
cd backend && pytest -m unit
cd backend && pytest -m integration

# Run with verbose output
cd backend && pytest -v

# Run with coverage
cd backend && pytest --cov=. --cov-report=html
```

### Frontend (Vue 3)

```bash
cd frontend

# Install dependencies
npm install

# Start development server (port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Code Style Guidelines

### Backend (Python/Django)

#### General
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **120 characters**
- Use **snake_case** for variable/function names
- Use **PascalCase** for class names
- Use **UPPER_SNAKE_CASE** for constants

#### Imports
Order imports as follows (PEP 8):
1. Standard library
2. Third-party packages
3. Django/DRF
4. Local application imports

```python
# Good import example
import uuid
from datetime import datetime

from django.db import models
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes

from apps.users.models import User
from apps.users.serializers import UserSerializer
```

#### Models
- Use UUID as primary key for most models: `id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`
- Add `created_at` and `updated_at` timestamps
- Use Chinese verbose names for admin interface
- Define `__str__` method for all models

```python
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username
```

#### Serializers
- Use `ModelSerializer` for simple cases
- Specify `read_only_fields` for auto-populated fields
- Use `write_only=True` for passwords

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
```

#### Views
- Use class-based views (CBV) for CRUD operations
- Use function-based views for custom actions
- Return consistent response format (see API Response Format below)

#### Error Handling
- Use DRF's `serializer.is_valid(raise_exception=True)` for automatic validation
- Use custom exception handler in `utils/exception_handler.py`
- Return consistent error format: `{'code': <int>, 'message': <str>, 'data': <any>}`

### Frontend (Vue 3)

#### General
- Use **Composition API** with `<script setup>`
- Use **2 spaces** for indentation in Vue/JS files
- Use **camelCase** for variables and functions
- Use **PascalCase** for components

#### Vue Component Structure
```vue
<template>
  <!-- Template content -->
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Component logic
</script>

<style scoped>
/* Component styles */
</style>
```

#### API Calls
- Use axios for HTTP requests
- Use API service modules in `@/api/`
- Handle errors with try/catch and show user feedback

```javascript
const fetchData = async () => {
  try {
    loading.value = true
    const data = await userApi.list(params)
    // Handle response
  } catch (error) {
    console.error('Failed to fetch:', error)
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}
```

#### Naming Conventions
- Components: `UserList.vue` (PascalCase)
- Props: `userId` (camelCase)
- Events: `update:modelValue` (kebab-case with v-model)
- CSS classes: `user-list`, `page-header` (kebab-case)

## API Response Format

All API responses follow this format:

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "meta": {
    "pagination": { ... }
  }
}
```

Error codes:
- `0`: Success
- `4001`: Authentication failed
- `400`: Validation error
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not found
- `500`: Server error

## Project Structure

```
backend/
├── apps/
│   ├── users/          # User management
│   ├── scenarios/      # Load test scenarios
│   ├── reports/        # Test reports
│   ├── environments/  # Environment variables
│   ├── datasources/    # Data sources
│   └── api_tests/      # API testing
├── config/             # Django configuration
├── utils/              # Utility functions
└── venv/               # Virtual environment

frontend/
├── src/
│   ├── api/           # API services
│   ├── components/    # Reusable components
│   ├── router/        # Vue Router
│   ├── store/         # Pinia stores
│   ├── views/         # Page components
│   └── utils/         # Utility functions
└── package.json
```

## Testing Guidelines

### Test File Location
- Backend tests: `apps/<app>/tests/test_<module>.py`
- Test naming: `<TestClassName>` and `test_<description>`

### Test Patterns
```python
class UserLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(...)
    
    def test_successful_login(self):
        """测试成功登录"""
        data = {'username': 'testuser', 'password': 'pass123'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Common Tasks

### Adding a New App
1. Create Django app: `python manage.py startapp <app_name>`
2. Add to `INSTALLED_APPS` in settings.py
3. Create models, serializers, views, urls
4. Register URLs in `config/urls.py`

### Adding a New API Endpoint
1. Create serializer in `apps/<app>/serializers.py`
2. Create view in `apps/<app>/views.py`
3. Add URL pattern in `apps/<app>/urls.py`
4. Include URLs in main `config/urls.py`

### Adding a New Vue Page
1. Create component in `frontend/src/views/<module>/`
2. Add route in `frontend/src/router/index.js`
3. Add API service in `frontend/src/api/`

## Git Commit Message Convention

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建/工具
```
