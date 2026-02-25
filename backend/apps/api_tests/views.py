import time
import requests
import re
import json
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import TestSuite, TestCase, Assertion, TestResult
from .serializers import (
    TestSuiteListSerializer, TestSuiteDetailSerializer, TestSuiteCreateUpdateSerializer,
    TestCaseListSerializer, TestCaseDetailSerializer, TestCaseCreateUpdateSerializer,
    AssertionSerializer, TestResultSerializer, ExecuteTestSerializer, SingleRequestSerializer
)


class TestSuiteListCreateView(generics.ListCreateAPIView):
    """测试套件列表/创建"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TestSuiteCreateUpdateSerializer
        return TestSuiteListSerializer
    
    def get_queryset(self):
        queryset = TestSuite.objects.filter(created_by=self.request.user, is_active=True)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """重写 list 方法，返回统一格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 0,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'page': self.paginator.page.number,
                    'page_size': self.paginator.page.paginator.per_page
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        suite = TestSuite.objects.get(id=serializer.instance.id)
        detail_serializer = TestSuiteDetailSerializer(suite)
        
        return Response({
            'code': 0,
            'message': '创建成功',
            'data': detail_serializer.data
        }, status=status.HTTP_201_CREATED)


class TestSuiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """测试套件详情/更新/删除"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TestSuiteCreateUpdateSerializer
        return TestSuiteDetailSerializer
    
    def get_queryset(self):
        return TestSuite.objects.filter(created_by=self.request.user, is_active=True)
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class TestCaseListCreateView(generics.ListCreateAPIView):
    """测试用例列表/创建"""
    serializer_class = TestCaseCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        suite_id = self.kwargs.get('suite_id')
        return TestCase.objects.filter(
            suite_id=suite_id,
            suite__created_by=self.request.user,
            is_active=True
        )
    
    def list(self, request, *args, **kwargs):
        """重写 list 方法，返回统一格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 0,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'page': self.paginator.page.number,
                    'page_size': self.paginator.page.paginator.per_page
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
    
    def perform_create(self, serializer):
        suite = get_object_or_404(
            TestSuite,
            pk=self.kwargs.get('suite_id'),
            created_by=self.request.user
        )
        serializer.save(suite=suite)


class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """测试用例详情/更新/删除"""
    serializer_class = TestCaseCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        return TestCase.objects.filter(
            suite__created_by=self.request.user,
            is_active=True
        )
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class AssertionListCreateView(generics.ListCreateAPIView):
    """断言列表/创建"""
    serializer_class = AssertionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        test_case_id = self.kwargs.get('test_case_id')
        return Assertion.objects.filter(
            test_case_id=test_case_id,
            test_case__suite__created_by=self.request.user,
            is_active=True
        )
    
    def list(self, request, *args, **kwargs):
        """重写 list 方法，返回统一格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 0,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'page': self.paginator.page.number,
                    'page_size': self.paginator.page.paginator.per_page
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
    
    def perform_create(self, serializer):
        test_case = get_object_or_404(
            TestCase,
            pk=self.kwargs.get('test_case_id'),
            suite__created_by=self.request.user
        )
        serializer.save(test_case=test_case)


class AssertionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """断言详情/更新/删除"""
    serializer_class = AssertionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        return Assertion.objects.filter(
            test_case__suite__created_by=self.request.user,
            is_active=True
        )
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class TestResultListView(generics.ListAPIView):
    """测试结果列表"""
    serializer_class = TestResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TestResult.objects.filter(
            test_case__suite__created_by=self.request.user
        )
        
        # 过滤
        test_case_id = self.request.query_params.get('test_case')
        if test_case_id:
            queryset = queryset.filter(test_case_id=test_case_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('test_case')
    
    def list(self, request, *args, **kwargs):
        """重写 list 方法，返回统一格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 0,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'page': self.paginator.page.number,
                    'page_size': self.paginator.page.paginator.per_page
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_test(request):
    """执行测试"""
    serializer = ExecuteTestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    test_case_id = serializer.validated_data.get('test_case_id')
    suite_id = serializer.validated_data.get('suite_id')
    
    if test_case_id:
        # 执行单个测试用例
        test_case = get_object_or_404(
            TestCase,
            pk=test_case_id,
            suite__created_by=request.user,
            is_active=True
        )
        result = execute_single_test(test_case)
        return Response({
            'code': 0,
            'message': '测试完成',
            'data': result
        })
    
    else:
        # 执行整个套件
        suite = get_object_or_404(
            TestSuite,
            pk=suite_id,
            created_by=request.user,
            is_active=True
        )
        
        results = []
        for test_case in suite.test_cases.filter(is_active=True).order_by('order'):
            result = execute_single_test(test_case)
            results.append(result)
        
        return Response({
            'code': 0,
            'message': '测试套件执行完成',
            'data': results
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_single_request(request):
    """执行单个请求（类似 Postman）"""
    serializer = SingleRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    data = serializer.validated_data
    assertions = data.get('assertions', [])
    
    try:
        # 发送请求
        start_time = time.time()
        response = requests.request(
            method=data['method'],
            url=data['url'],
            headers=data.get('headers', {}),
            data=data.get('body') if data.get('body') else None,
            timeout=30
        )
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 执行断言
        assertion_results = []
        for assertion in assertions:
            result = evaluate_assertion(assertion, response, response_time)
            assertion_results.append(result)
        
        # 判断整体结果
        all_passed = all(r['passed'] for r in assertion_results)
        
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'status': 'passed' if all_passed else 'failed',
                'response_status': response.status_code,
                'response_time': round(response_time, 2),
                'response_headers': dict(response.headers),
                'response_body': response.text[:10000],  # 限制返回大小
                'assertion_results': assertion_results
            }
        })
    
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'请求失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def execute_single_test(test_case):
    """执行单个测试用例"""
    try:
        # 发送请求
        start_time = time.time()
        response = requests.request(
            method=test_case.method,
            url=test_case.url,
            headers=test_case.headers if test_case.headers else {},
            data=test_case.body if test_case.body else None,
            timeout=30
        )
        response_time = (time.time() - start_time) * 1000
        
        # 执行断言
        assertion_results = []
        for assertion in test_case.assertions.filter(is_active=True):
            result = evaluate_assertion(assertion, response, response_time)
            assertion_results.append(result)
        
        # 判断整体结果
        all_passed = all(r['passed'] for r in assertion_results)
        status_result = 'passed' if all_passed else 'failed'
        
        # 保存结果
        test_result = TestResult.objects.create(
            test_case=test_case,
            status=status_result,
            request_headers=test_case.headers,
            request_body=test_case.body,
            response_status=response.status_code,
            response_headers=dict(response.headers),
            response_body=response.text[:10000],
            response_time=response_time,
            assertion_results=assertion_results
        )
        
        return {
            'id': str(test_result.id),
            'test_case_id': str(test_case.id),
            'test_case_name': test_case.name,
            'status': status_result,
            'response_status': response.status_code,
            'response_time': round(response_time, 2),
            'assertion_results': assertion_results
        }
    
    except Exception as e:
        # 保存失败结果
        test_result = TestResult.objects.create(
            test_case=test_case,
            status='error',
            request_headers=test_case.headers,
            request_body=test_case.body,
            response_status=0,
            response_time=0,
            error_message=str(e)
        )
        
        return {
            'id': str(test_result.id),
            'test_case_id': str(test_case.id),
            'test_case_name': test_case.name,
            'status': 'error',
            'error_message': str(e)
        }


def evaluate_assertion(assertion, response, response_time):
    """评估断言"""
    assertion_type = assertion.assertion_type
    expected_value = assertion.expected_value
    operator = assertion.operator
    
    result = {
        'assertion_name': assertion.name,
        'assertion_type': assertion_type,
        'passed': False,
        'expected': expected_value,
        'actual': None
    }
    
    try:
        if assertion_type == 'status_code':
            actual_value = response.status_code
            result['actual'] = actual_value
            result['passed'] = compare_values(actual_value, expected_value, operator)
        
        elif assertion_type == 'response_time':
            actual_value = response_time
            result['actual'] = round(actual_value, 2)
            result['passed'] = compare_values(actual_value, expected_value, operator)
        
        elif assertion_type == 'json_path':
            try:
                json_data = response.json()
                actual_value = get_json_path(json_data, assertion.target_path)
                result['actual'] = actual_value
                result['passed'] = compare_values(actual_value, expected_value, operator)
            except:
                result['actual'] = '无法解析JSON'
                result['passed'] = False
        
        elif assertion_type == 'regex':
            pattern = expected_value
            actual_value = response.text
            result['actual'] = actual_value[:200]  # 限制显示长度
            result['passed'] = bool(re.search(pattern, actual_value))
        
        elif assertion_type == 'contains':
            actual_value = response.text
            result['actual'] = actual_value[:200]
            result['passed'] = expected_value in actual_value
        
        elif assertion_type == 'numeric_range':
            try:
                actual_value = float(response.text) if response.text else 0
                result['actual'] = actual_value
                min_val = assertion.min_value
                max_val = assertion.max_value
                result['passed'] = (min_val is None or actual_value >= min_val) and \
                                  (max_val is None or actual_value <= max_val)
            except:
                result['actual'] = '非数值'
                result['passed'] = False
    
    except Exception as e:
        result['actual'] = f'错误: {str(e)}'
        result['passed'] = False
    
    return result


def compare_values(actual, expected, operator):
    """比较值"""
    try:
        # 尝试转换为数值
        try:
            actual_val = float(actual)
            expected_val = float(expected)
        except:
            actual_val = str(actual)
            expected_val = str(expected)
        
        if operator == 'eq':
            return actual_val == expected_val
        elif operator == 'ne':
            return actual_val != expected_val
        elif operator == 'gt':
            return actual_val > expected_val
        elif operator == 'gte':
            return actual_val >= expected_val
        elif operator == 'lt':
            return actual_val < expected_val
        elif operator == 'lte':
            return actual_val <= expected_val
        elif operator == 'contains':
            return expected_val in str(actual_val)
        elif operator == 'regex':
            return bool(re.search(expected, str(actual)))
        
        return False
    except:
        return False


def get_json_path(data, path):
    """获取 JSON 路径值"""
    # 支持简单的点号路径，如 data.user.id
    keys = path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    
    return value
