from rest_framework import serializers
from .models import Scenario, Request, HARImport


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            "id",
            "name",
            "method",
            "url",
            "headers",
            "body_type",
            "body",
            "weight",
            "think_time",
            "timeout",
            "order",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HARImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HARImport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ScenarioListSerializer(serializers.ModelSerializer):
    """场景列表序列化器"""

    request_count = serializers.IntegerField(source="requests.count", read_only=True)

    class Meta:
        model = Scenario
        fields = [
            "id",
            "name",
            "description",
            "request_count",
            "is_imported_from_har",
            "target_host",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ScenarioDetailSerializer(serializers.ModelSerializer):
    """场景详情序列化器"""

    requests = RequestSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Scenario
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


class ScenarioCreateUpdateSerializer(serializers.ModelSerializer):
    """场景创建/更新序列化器"""

    requests = RequestSerializer(many=True, required=False)

    class Meta:
        model = Scenario
        fields = [
            "name",
            "description",
            "target_host",
            "default_users",
            "default_spawn_rate",
            "default_duration",
            "requests",
        ]

    def create(self, validated_data):
        requests_data = validated_data.pop("requests", [])
        scenario = Scenario.objects.create(**validated_data)

        for i, request_data in enumerate(requests_data):
            Request.objects.create(scenario=scenario, order=i, **request_data)

        return scenario

    def update(self, instance, validated_data):
        requests_data = validated_data.pop("requests", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if requests_data is not None:
            # 删除旧请求
            instance.requests.all().delete()
            # 创建新请求
            for i, request_data in enumerate(requests_data):
                Request.objects.create(scenario=instance, order=i, **request_data)

        return instance
