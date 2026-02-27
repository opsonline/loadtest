import uuid
from django.db import models
from apps.users.models import User


class Scenario(models.Model):
    """压测场景"""

    HTTP_METHODS = [
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("PATCH", "PATCH"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="场景名称")
    description = models.TextField(blank=True, null=True, verbose_name="场景描述")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="scenarios"
    )

    # HAR 导入相关
    is_imported_from_har = models.BooleanField(
        default=False, verbose_name="是否从HAR导入"
    )
    har_file_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="HAR文件名"
    )

    # 压测目标配置
    target_host = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="目标Host"
    )

    # 压测配置
    default_users = models.IntegerField(default=10, verbose_name="默认用户数")
    default_spawn_rate = models.IntegerField(
        default=1, verbose_name="默认每秒生成用户数"
    )
    default_duration = models.IntegerField(default=60, verbose_name="默认压测时长(秒)")

    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "scenarios"
        verbose_name = "压测场景"
        verbose_name_plural = "压测场景"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Request(models.Model):
    """场景中的请求"""

    HTTP_METHODS = [
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("PATCH", "PATCH"),
    ]

    BODY_TYPES = [
        ("none", "无"),
        ("json", "JSON"),
        ("form", "表单"),
        ("file", "文件"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="requests"
    )
    name = models.CharField(max_length=200, verbose_name="请求名称")
    method = models.CharField(
        max_length=10, choices=HTTP_METHODS, default="GET", verbose_name="请求方法"
    )
    url = models.TextField(verbose_name="请求URL")
    headers = models.JSONField(default=dict, blank=True, verbose_name="请求头")
    body_type = models.CharField(
        max_length=10, choices=BODY_TYPES, default="none", verbose_name="请求体类型"
    )
    body = models.TextField(blank=True, null=True, verbose_name="请求体")

    # 请求配置
    weight = models.IntegerField(default=1, verbose_name="权重")
    think_time = models.FloatField(default=1.0, verbose_name="思考时间(秒)")
    timeout = models.IntegerField(default=30, verbose_name="超时时间(秒)")

    # 数据源绑定
    datasource = models.ForeignKey(
        "datasources.DataSource",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
    )
    datasource_mapping = models.JSONField(
        default=dict, blank=True, verbose_name="数据源映射"
    )

    order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "requests"
        verbose_name = "请求"
        verbose_name_plural = "请求"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.name} ({self.method})"


class HARImport(models.Model):
    """HAR 导入记录"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="har_imports"
    )
    file_name = models.CharField(max_length=255, verbose_name="文件名")
    file_path = models.CharField(max_length=500, verbose_name="文件路径")
    resource_types = models.JSONField(default=list, verbose_name="资源类型过滤")
    host_replacement = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="Host替换"
    )
    imported_count = models.IntegerField(default=0, verbose_name="导入请求数")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "har_imports"
        verbose_name = "HAR导入记录"
        verbose_name_plural = "HAR导入记录"
