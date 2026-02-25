import uuid
from django.db import models
from apps.users.models import User


class DataSource(models.Model):
    """数据源"""
    SOURCE_TYPES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('mysql', 'MySQL'),
        ('postgresql', 'PostgreSQL'),
        ('mongodb', 'MongoDB'),
        ('redis', 'Redis'),
        ('python', 'Python脚本'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='数据源名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name='数据源类型')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasources')
    
    # 文件类型数据源
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='文件路径')
    file_encoding = models.CharField(max_length=20, default='utf-8', verbose_name='文件编码')
    csv_delimiter = models.CharField(max_length=10, default=',', verbose_name='CSV分隔符')
    
    # 数据库类型数据源
    db_host = models.CharField(max_length=255, blank=True, null=True, verbose_name='主机')
    db_port = models.IntegerField(null=True, blank=True, verbose_name='端口')
    db_user = models.CharField(max_length=100, blank=True, null=True, verbose_name='用户名')
    db_password = models.CharField(max_length=255, blank=True, null=True, verbose_name='密码')
    db_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='数据库名')
    db_query = models.TextField(blank=True, null=True, verbose_name='查询语句')
    db_collection = models.CharField(max_length=100, blank=True, null=True, verbose_name='集合/表名')
    redis_key = models.CharField(max_length=255, blank=True, null=True, verbose_name='Redis键')
    redis_pattern = models.CharField(max_length=255, blank=True, null=True, verbose_name='Redis匹配模式')
    
    # Python脚本
    python_script = models.TextField(blank=True, null=True, verbose_name='Python脚本')
    
    # 预览数据（前N行）
    preview_data = models.JSONField(default=list, blank=True, verbose_name='预览数据')
    total_count = models.IntegerField(default=0, verbose_name='数据总数')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'datasources'
        verbose_name = '数据源'
        verbose_name_plural = '数据源'

    def __str__(self):
        return self.name
