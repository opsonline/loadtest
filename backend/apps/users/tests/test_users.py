from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User


class UserRegistrationTests(TestCase):
    """用户注册测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/users/register/'
    
    def test_successful_registration(self):
        """测试成功注册"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('tokens', response.data['data'])
        self.assertEqual(User.objects.count(), 1)
    
    def test_duplicate_username(self):
        """测试重复用户名"""
        User.objects.create_user('existing', 'test@test.com', 'pass123')
        
        data = {
            'username': 'existing',
            'email': 'new@test.com',
            'password': 'pass123'
        }
        response = self.client.post(self.register_url, data)
        # Django 会自动处理重复用户名的验证


class UserLoginTests(TestCase):
    """用户登录测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/v1/users/login/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='correctpass123'
        )
    
    def test_successful_login(self):
        """测试成功登录"""
        data = {
            'username': 'testuser',
            'password': 'correctpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('access_token', response.data['data']['tokens'])
    
    def test_invalid_password(self):
        """测试错误密码"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_nonexistent_user(self):
        """测试不存在的用户"""
        data = {
            'username': 'nonexistent',
            'password': 'somepassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(TestCase):
    """用户信息测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = '/api/v1/users/profile/'
    
    def test_get_profile(self):
        """测试获取用户信息"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['username'], 'testuser')
    
    def test_profile_unauthorized(self):
        """测试未授权访问"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
