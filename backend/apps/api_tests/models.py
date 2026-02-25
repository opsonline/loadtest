import uuid
from django.db import models
from apps.users.models import User


class TestSuite(models.Model):
    """测试套件"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='套件名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_suites')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test_suites'
        verbose_name = '测试套件'
        verbose_name_plural = '测试套件'

    def __str__(self):
        return self.name


class TestCase(models.Model):
    """测试用例"""
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, related_name='test_cases')
    name = models.CharField(max_length=200, verbose_name='用例名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    method = models.CharField(max_length=10, choices=HTTP_METHODS, default='GET', verbose_name='请求方法')
    url = models.TextField(verbose_name='请求URL')
    headers = models.JSONField(default=dict, blank=True, verbose_name='请求头')
    body = models.TextField(blank=True, null=True, verbose_name='请求体')
    
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test_cases'
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name


class Assertion(models.Model):
    """断言规则"""
    ASSERTION_TYPES = [
        ('status_code', '状态码'),
        ('response_time', '响应时间'),
        ('json_path', 'JSON路径'),
        ('regex', '正则匹配'),
        ('contains', '包含验证'),
        ('numeric_range', '数值范围'),
    ]

    OPERATORS = [
        ('eq', '等于'),
        ('ne', '不等于'),
        ('gt', '大于'),
        ('gte', '大于等于'),
        ('lt', '小于'),
        ('lte', '小于等于'),
        ('contains', '包含'),
        ('regex', '匹配正则'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='assertions')
    name = models.CharField(max_length=200, verbose_name='断言名称')
    assertion_type = models.CharField(max_length=20, choices=ASSERTION_TYPES, verbose_name='断言类型')
    
    # 根据类型不同的字段
    target_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='目标路径（JSON Path）')
    expected_value = models.TextField(verbose_name='预期值')
    operator = models.CharField(max_length=20, choices=OPERATORS, default='eq', verbose_name='操作符')
    
    # 数值范围专用
    min_value = models.FloatField(null=True, blank=True, verbose_name='最小值')
    max_value = models.FloatField(null=True, blank=True, verbose_name='最大值')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assertions'
        verbose_name = '断言规则'
        verbose_name_plural = '断言规则'

    def __str__(self):
        return self.name


class TestResult(models.Model):
    """测试结果"""
    RESULT_STATUS = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('error', '错误'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='test_results')
    status = models.CharField(max_length=20, choices=RESULT_STATUS, verbose_name='状态')
    
    # 请求信息
    request_headers = models.JSONField(default=dict, blank=True, verbose_name='请求头')
    request_body = models.TextField(blank=True, null=True, verbose_name='请求体')
    
    # 响应信息
    response_status = models.IntegerField(verbose_name='响应状态码')
    response_headers = models.JSONField(default=dict, blank=True, verbose_name='响应头')
    response_body = models.TextField(blank=True, null=True, verbose_name='响应体')
    response_time = models.FloatField(verbose_name='响应时间(ms)')
    
    # 断言结果
    assertion_results = models.JSONField(default=list, verbose_name='断言结果')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_results'
        verbose_name = '测试结果'
        verbose_name_plural = '测试结果'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.test_case.name} - {self.status}"
