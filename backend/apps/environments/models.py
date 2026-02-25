import uuid
from django.db import models
from apps.users.models import User


class Environment(models.Model):
    """环境配置"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='环境名称')
    description = models.TextField(blank=True, null=True, verbose_name='环境描述')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='environments')
    is_default = models.BooleanField(default=False, verbose_name='是否默认环境')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'environments'
        verbose_name = '环境'
        verbose_name_plural = '环境'

    def __str__(self):
        return self.name


class Variable(models.Model):
    """环境变量"""
    VAR_TYPES = [
        ('text', '文本'),
        ('secret', '敏感'),
        ('reference', '引用'),
    ]

    SCOPES = [
        ('global', '全局'),
        ('project', '项目'),
        ('scenario', '场景'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='variables')
    name = models.CharField(max_length=100, verbose_name='变量名')
    value = models.TextField(verbose_name='变量值')
    var_type = models.CharField(max_length=20, choices=VAR_TYPES, default='text', verbose_name='变量类型')
    scope = models.CharField(max_length=20, choices=SCOPES, default='global', verbose_name='作用域')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'variables'
        verbose_name = '变量'
        verbose_name_plural = '变量'
        unique_together = ['environment', 'name']

    def __str__(self):
        return f"{self.name} ({self.environment.name})"
