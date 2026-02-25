import uuid
from django.db import models
from apps.users.models import User
from apps.scenarios.models import Scenario


class Report(models.Model):
    """压测报告"""
    STATUS_CHOICES = [
        ('pending', '待运行'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('stopped', '已停止'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=200, verbose_name='报告名称')
    description = models.TextField(blank=True, null=True, verbose_name='报告描述')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    
    # 运行配置
    users = models.IntegerField(verbose_name='并发用户数')
    spawn_rate = models.IntegerField(verbose_name='每秒生成用户数')
    duration = models.IntegerField(verbose_name='压测时长(秒)')
    
    # 运行状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    
    # 总体统计
    total_requests = models.BigIntegerField(default=0, verbose_name='总请求数')
    total_failures = models.BigIntegerField(default=0, verbose_name='失败请求数')
    success_rate = models.FloatField(default=0, verbose_name='成功率(%)')
    avg_response_time = models.FloatField(default=0, verbose_name='平均响应时间(ms)')
    min_response_time = models.FloatField(default=0, verbose_name='最小响应时间(ms)')
    max_response_time = models.FloatField(default=0, verbose_name='最大响应时间(ms)')
    p50_response_time = models.FloatField(default=0, verbose_name='P50响应时间(ms)')
    p90_response_time = models.FloatField(default=0, verbose_name='P90响应时间(ms)')
    p95_response_time = models.FloatField(default=0, verbose_name='P95响应时间(ms)')
    p99_response_time = models.FloatField(default=0, verbose_name='P99响应时间(ms)')
    rps = models.FloatField(default=0, verbose_name='RPS')
    
    # 错误分布
    error_distribution = models.JSONField(default=dict, verbose_name='错误分布')
    
    # 原始数据文件
    stats_file = models.CharField(max_length=500, blank=True, null=True, verbose_name='统计数据文件')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports'
        verbose_name = '压测报告'
        verbose_name_plural = '压测报告'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class RequestStats(models.Model):
    """请求级别的统计"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='request_stats')
    request_name = models.CharField(max_length=200, verbose_name='请求名称')
    method = models.CharField(max_length=10, verbose_name='请求方法')
    url = models.TextField(verbose_name='请求URL')
    
    # 统计
    num_requests = models.BigIntegerField(default=0, verbose_name='请求数')
    num_failures = models.BigIntegerField(default=0, verbose_name='失败数')
    avg_response_time = models.FloatField(default=0, verbose_name='平均响应时间(ms)')
    min_response_time = models.FloatField(default=0, verbose_name='最小响应时间(ms)')
    max_response_time = models.FloatField(default=0, verbose_name='最大响应时间(ms)')
    p50_response_time = models.FloatField(default=0, verbose_name='P50响应时间(ms)')
    p90_response_time = models.FloatField(default=0, verbose_name='P90响应时间(ms)')
    p95_response_time = models.FloatField(default=0, verbose_name='P95响应时间(ms)')
    p99_response_time = models.FloatField(default=0, verbose_name='P99响应时间(ms)')
    
    # 响应时间分布
    response_time_distribution = models.JSONField(default=dict, verbose_name='响应时间分布')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'request_stats'
        verbose_name = '请求统计'
        verbose_name_plural = '请求统计'
