from rest_framework import serializers
from .models import DataSource


class DataSourceListSerializer(serializers.ModelSerializer):
    """数据源列表序列化器"""
    
    class Meta:
        model = DataSource
        fields = ['id', 'name', 'source_type', 'total_count', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class DataSourceDetailSerializer(serializers.ModelSerializer):
    """数据源详情序列化器"""
    # 隐藏敏感信息
    db_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = DataSource
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'preview_data', 'total_count']


class DataSourceCreateUpdateSerializer(serializers.ModelSerializer):
    """数据源创建/更新序列化器"""
    db_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = DataSource
        fields = ['name', 'description', 'source_type', 'file_path', 'file_encoding',
                  'csv_delimiter', 'db_host', 'db_port', 'db_user', 'db_password',
                  'db_name', 'db_query', 'db_collection', 'redis_key', 'redis_pattern',
                  'python_script']
    
    def validate(self, data):
        source_type = data.get('source_type')
        
        # 根据数据源类型验证必填字段
        if source_type in ['csv', 'json']:
            if not data.get('file_path'):
                raise serializers.ValidationError('文件路径不能为空')
        
        elif source_type in ['mysql', 'postgresql']:
            required_fields = ['db_host', 'db_port', 'db_user', 'db_name', 'db_query']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f'{field} 不能为空')
        
        elif source_type == 'mongodb':
            required_fields = ['db_host', 'db_port', 'db_name', 'db_collection']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f'{field} 不能为空')
        
        elif source_type == 'redis':
            if not data.get('db_host'):
                raise serializers.ValidationError('主机不能为空')
        
        elif source_type == 'python':
            if not data.get('python_script'):
                raise serializers.ValidationError('Python脚本不能为空')
        
        return data


class DataSourcePreviewSerializer(serializers.Serializer):
    """数据源预览序列化器"""
    data = serializers.ListField(child=serializers.DictField())
    total_count = serializers.IntegerField()
