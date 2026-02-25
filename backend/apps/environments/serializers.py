from rest_framework import serializers
from .models import Environment, Variable


class VariableSerializer(serializers.ModelSerializer):
    """环境变量序列化器"""
    
    class Meta:
        model = Variable
        fields = ['id', 'name', 'value', 'var_type', 'scope', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnvironmentListSerializer(serializers.ModelSerializer):
    """环境列表序列化器"""
    variable_count = serializers.IntegerField(source='variables.count', read_only=True)
    
    class Meta:
        model = Environment
        fields = ['id', 'name', 'description', 'is_default', 'is_active', 'variable_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class EnvironmentDetailSerializer(serializers.ModelSerializer):
    """环境详情序列化器"""
    variables = VariableSerializer(many=True, read_only=True)
    
    class Meta:
        model = Environment
        fields = ['id', 'name', 'description', 'is_default', 'is_active', 'variables', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnvironmentCreateUpdateSerializer(serializers.ModelSerializer):
    """环境创建/更新序列化器"""
    variables = VariableSerializer(many=True, required=False)
    
    class Meta:
        model = Environment
        fields = ['name', 'description', 'is_default', 'variables']
    
    def create(self, validated_data):
        variables_data = validated_data.pop('variables', [])
        environment = Environment.objects.create(**validated_data)
        
        for var_data in variables_data:
            Variable.objects.create(environment=environment, **var_data)
        
        return environment
    
    def update(self, instance, validated_data):
        variables_data = validated_data.pop('variables', None)
        
        # 如果设置为默认环境，取消其他默认环境
        if validated_data.get('is_default') and not instance.is_default:
            Environment.objects.filter(created_by=instance.created_by, is_default=True).update(is_default=False)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if variables_data is not None:
            instance.variables.all().delete()
            for var_data in variables_data:
                Variable.objects.create(environment=instance, **var_data)
        
        return instance
