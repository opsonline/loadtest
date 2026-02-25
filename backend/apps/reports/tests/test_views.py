import pytest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apps.users.models import User
from apps.scenarios.models import Scenario
from apps.reports.models import Report, RequestStats
from unittest.mock import patch


@pytest.mark.django_db
class ReportAPITests(APITestCase):
    """报告API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试场景
        self.scenario = Scenario.objects.create(
            name='测试场景',
            description='用于测试的场景',
            created_by=self.user,
            default_users=10,
            default_spawn_rate=1,
            default_duration=60
        )
    
    def test_create_report(self):
        """测试创建报告"""
        data = {
            'scenario_id': str(self.scenario.id),
            'name': '测试报告',
            'users': 10,
            'spawn_rate': 1,
            'duration': 60
        }
        response = self.client.post('/api/v1/reports/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(response.data['data']['name'], '测试报告')
    
    def test_list_reports(self):
        """测试获取报告列表"""
        Report.objects.create(
            scenario=self.scenario,
            name='报告1',
            users=10,
            spawn_rate=1,
            duration=60,
            created_by=self.user
        )
        
        response = self.client.get('/api/v1/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_report_detail(self):
        """测试获取报告详情"""
        report = Report.objects.create(
            scenario=self.scenario,
            name='报告详情测试',
            users=10,
            spawn_rate=1,
            duration=60,
            created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/reports/{report.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], '报告详情测试')
    
    def test_delete_report(self):
        """测试删除报告"""
        report = Report.objects.create(
            scenario=self.scenario,
            name='要删除的报告',
            users=10,
            spawn_rate=1,
            duration=60,
            created_by=self.user
        )
        
        response = self.client.delete(f'/api/v1/reports/{report.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Report.DoesNotExist):
            Report.objects.get(id=report.id)
    
    def test_export_report_pdf(self):
        """测试导出报告为PDF"""
        report = Report.objects.create(
            scenario=self.scenario,
            name='PDF导出测试',
            users=10,
            spawn_rate=1,
            duration=60,
            created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/reports/{report.id}/export/pdf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Type'), 'application/pdf')
    
    def test_export_report_excel(self):
        """测试导出报告为Excel"""
        report = Report.objects.create(
            scenario=self.scenario,
            name='Excel导出测试',
            users=10,
            spawn_rate=1,
            duration=60,
            created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/reports/{report.id}/export/excel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.get('Content-Type'), 
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


@pytest.mark.django_db
class ReportPermissionTests(APITestCase):
    """报告权限测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.owner_user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        self.scenario = Scenario.objects.create(
            name='测试场景',
            description='用于测试的场景',
            created_by=self.owner_user,
            default_users=10,
            default_spawn_rate=1,
            default_duration=60
        )
        self.report = Report.objects.create(
            scenario=self.scenario,
            name='测试报告',
            users=10,
            spawn_rate=1,
            duration=60,
            created_by=self.owner_user
        )
    
    def test_owner_can_access_report(self):
        """测试报告所有者可以访问报告"""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(f'/api/v1/reports/{self.report.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_non_owner_cannot_access_report(self):
        """测试非所有者不能访问报告"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/v1/reports/{self.report.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_non_owner_cannot_delete_report(self):
        """测试非所有者不能删除报告"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f'/api/v1/reports/{self.report.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class RequestStatsTests(TestCase):
    """请求统计测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.scenario = Scenario.objects.create(
            name='测试场景',
            description='用于测试的场景',
            created_by=self.user,
            default_users=10,
            default_spawn_rate=1,
            default_duration=60
        )
        self.report = Report.objects.create(
            scenario=self.scenario,
            name='测试报告',
            users=10,
            spawn_rate=1,
            duration=60,
            created_by=self.user
        )
    
    def test_create_request_stats(self):
        """测试创建请求统计"""
        stats = RequestStats.objects.create(
            report=self.report,
            request_name='测试接口',
            method='GET',
            url='/api/test/',
            num_requests=100,
            num_failures=5,
            avg_response_time=150.0,
            min_response_time=50.0,
            max_response_time=500.0,
            p50_response_time=120.0,
            p90_response_time=250.0,
            p95_response_time=300.0,
            p99_response_time=400.0
        )
        
        self.assertEqual(stats.request_name, '测试接口')
        self.assertEqual(stats.num_requests, 100)
        self.assertAlmostEqual(stats.avg_response_time, 150.0)
    
    def test_request_stats_association_with_report(self):
        """测试请求统计与报告的关联"""
        stats = RequestStats.objects.create(
            report=self.report,
            request_name='关联测试',
            method='POST',
            url='/api/test/',
            num_requests=50
        )
        
        self.assertEqual(stats.report, self.report)
        self.assertEqual(self.report.requeststats_set.count(), 1)