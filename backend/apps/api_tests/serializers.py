from rest_framework import serializers
from .models import TestSuite, TestCase, Assertion, TestResult


class AssertionSerializer(serializers.ModelSerializer):
    """断言序列化器"""
    
    class Meta:
        model = Assertion
        fields = ['id', 'name', 'assertion_type', 'target_path', 'expected_value', 
                  'operator', 'min_value', 'max_value', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TestCaseListSerializer(serializers.ModelSerializer):
    """测试用例列表序列化器"""
    assertion_count = serializers.IntegerField(source='assertions.count', read_only=True)
    
    class Meta:
        model = TestCase
        fields = ['id', 'name', 'description', 'method', 'url', 'assertion_count', 'order', 'is_active']
        read_only_fields = ['id']


class TestCaseDetailSerializer(serializers.ModelSerializer):
    """测试用例详情序列化器"""
    assertions = AssertionSerializer(many=True, read_only=True)
    
    class Meta:
        model = TestCase
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestCaseCreateUpdateSerializer(serializers.ModelSerializer):
    """测试用例创建/更新序列化器"""
    assertions = AssertionSerializer(many=True, required=False)
    
    class Meta:
        model = TestCase
        fields = ['name', 'description', 'method', 'url', 'headers', 'body', 
                  'order', 'is_active', 'assertions']
    
    def create(self, validated_data):
        assertions_data = validated_data.pop('assertions', [])
        test_case = TestCase.objects.create(**validated_data)
        
        for assertion_data in assertions_data:
            Assertion.objects.create(test_case=test_case, **assertion_data)
        
        return test_case
    
    def update(self, instance, validated_data):
        assertions_data = validated_data.pop('assertions', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if assertions_data is not None:
            instance.assertions.all().delete()
            for assertion_data in assertions_data:
                Assertion.objects.create(test_case=instance, **assertion_data)
        
        return instance


class TestSuiteListSerializer(serializers.ModelSerializer):
    """测试套件列表序列化器"""
    test_case_count = serializers.IntegerField(source='test_cases.count', read_only=True)
    
    class Meta:
        model = TestSuite
        fields = ['id', 'name', 'description', 'test_case_count', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TestSuiteDetailSerializer(serializers.ModelSerializer):
    """测试套件详情序列化器"""
    test_cases = TestCaseListSerializer(many=True, read_only=True)
    
    class Meta:
        model = TestSuite
        fields = ['id', 'name', 'description', 'is_active', 'test_cases', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestSuiteCreateUpdateSerializer(serializers.ModelSerializer):
    """测试套件创建/更新序列化器"""
    
    class Meta:
        model = TestSuite
        fields = ['name', 'description', 'is_active']


class TestResultSerializer(serializers.ModelSerializer):
    """测试结果序列化器"""
    test_case_name = serializers.CharField(source='test_case.name', read_only=True)
    
    class Meta:
        model = TestResult
        fields = ['id', 'test_case', 'test_case_name', 'status', 'response_status',
                  'response_time', 'assertion_results', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExecuteTestSerializer(serializers.Serializer):
    """执行测试序列化器"""
    test_case_id = serializers.UUIDField(required=False)
    suite_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        if not data.get('test_case_id') and not data.get('suite_id'):
            raise serializers.ValidationError('请提供 test_case_id 或 suite_id')
        return data


class SingleRequestSerializer(serializers.Serializer):
    """单个请求测试序列化器"""
    method = serializers.ChoiceField(choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    url = serializers.URLField()
    headers = serializers.DictField(required=False, default=dict)
    body = serializers.CharField(required=False, allow_blank=True)
    assertions = AssertionSerializer(many=True, required=False)
