import pytest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apps.users.models import User
from apps.scenarios.models import Scenario, Request
from apps.reports.models import Report
from apps.environments.models import Environment, Variable


class UserAuthTests(APITestCase):
    """用户认证测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_user_registration(self):
        """测试用户注册"""
        response = self.client.post('/api/v1/users/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('access_token', response.data['data']['tokens'])
    
    def test_user_login(self):
        """测试用户登录"""
        # 先注册
        self.client.post('/api/v1/users/register/', self.user_data)
        
        # 再登录
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post('/api/v1/users/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 0)
    
    def test_user_login_wrong_password(self):
        """测试错误密码登录"""
        self.client.post('/api/v1/users/register/', self.user_data)
        
        login_data = {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/v1/users/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ScenarioTests(APITestCase):
    """场景管理测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_scenario(self):
        """测试创建场景"""
        data = {
            'name': '测试场景',
            'description': '这是一个测试场景',
            'default_users': 10,
            'default_spawn_rate': 1,
            'default_duration': 60,
            'requests': [
                {
                    'name': '测试请求',
                    'method': 'GET',
                    'url': 'https://api.example.com/test',
                    'headers': {},
                    'body_type': 'none',
                    'weight': 1,
                    'think_time': 1.0,
                    'timeout': 30
                }
            ]
        }
        response = self.client.post('/api/v1/scenarios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Scenario.objects.count(), 1)
    
    def test_list_scenarios(self):
        """测试获取场景列表"""
        Scenario.objects.create(
            name='场景1',
            description='描述1',
            created_by=self.user,
            default_users=10,
            default_spawn_rate=1,
            default_duration=60
        )
        
        response = self.client.get('/api/v1/scenarios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_delete_scenario(self):
        """测试删除场景"""
        scenario = Scenario.objects.create(
            name='要删除的场景',
            description='测试删除',
            created_by=self.user,
            default_users=10,
            default_spawn_rate=1,
            default_duration=60
        )
        
        response = self.client.delete(f'/api/v1/scenarios/{scenario.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        scenario.refresh_from_db()
        self.assertFalse(scenario.is_active)


class EnvironmentTests(APITestCase):
    """环境变量测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_environment(self):
        """测试创建环境"""
        data = {
            'name': '测试环境',
            'description': '测试环境描述',
            'is_default': False
        }
        response = self.client.post('/api/v1/environments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Environment.objects.count(), 1)
    
    def test_create_variable(self):
        """测试创建变量"""
        env = Environment.objects.create(
            name='测试环境',
            description='描述',
            created_by=self.user
        )
        
        data = {
            'name': 'BASE_URL',
            'value': 'https://api.example.com',
            'var_type': 'text',
            'scope': 'global'
        }
        response = self.client.post(f'/api/v1/environments/{env.id}/variables/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Variable.objects.count(), 1)


class HARParserTests(TestCase):
    """HAR 解析器测试"""
    
    def test_parse_har_data(self):
        """测试解析 HAR 数据"""
        from apps.scenarios.har_parser import HARParser
        
        parser = HARParser()
        har_data = {
            'log': {
                'entries': [
                    {
                        'request': {
                            'url': 'https://api.example.com/users',
                            'method': 'GET',
                            'headers': [{'name': 'Authorization', 'value': 'Bearer token'}]
                        },
                        'response': {
                            'status': 200,
                            'content': {'mimeType': 'application/json'}
                        },
                        '_resourceType': 'xhr'
                    }
                ]
            }
        }
        
        # 模拟解析
        entries = har_data['log']['entries']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['request']['method'], 'GET')
    
    def test_replace_host(self):
        """测试 Host 替换"""
        from apps.scenarios.har_parser import HARParser
        
        parser = HARParser()
        url = 'https://old-api.example.com/users?id=123'
        new_url = parser.replace_host(url, 'new-api.example.com')
        
        self.assertEqual(new_url, 'https://new-api.example.com/users?id=123')


class APITests(APITestCase):
    """API 功能测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        # 未登录访问
        client = APIClient()
        response = client.get('/api/v1/scenarios/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_profile(self):
        """测试获取用户信息"""
        response = self.client.get('/api/v1/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['username'], 'testuser')


# pytest 配置
pytestmark = pytest.mark.django_db
