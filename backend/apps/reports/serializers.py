from rest_framework import serializers
from .models import Report, RequestStats


class RequestStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestStats
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ReportListSerializer(serializers.ModelSerializer):
    """报告列表序列化器"""
    scenario_name = serializers.CharField(source='scenario.name', read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'name', 'scenario', 'scenario_name', 'status', 'users', 
                  'duration', 'total_requests', 'success_rate', 'rps', 
                  'avg_response_time', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReportDetailSerializer(serializers.ModelSerializer):
    """报告详情序列化器"""
    scenario_name = serializers.CharField(source='scenario.name', read_only=True)
    request_stats = RequestStatsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'started_at', 'ended_at']


class ReportCreateSerializer(serializers.ModelSerializer):
    """创建报告序列化器"""
    
    class Meta:
        model = Report
        fields = ['scenario', 'name', 'description', 'users', 'spawn_rate', 'duration']


class ReportRunSerializer(serializers.Serializer):
    """运行压测序列化器"""
    users = serializers.IntegerField(min_value=1, max_value=10000, default=10)
    spawn_rate = serializers.IntegerField(min_value=1, max_value=1000, default=1)
    duration = serializers.IntegerField(min_value=1, max_value=3600, default=60)
