import csv
import json
import io
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import DataSource
from .serializers import (
    DataSourceListSerializer, DataSourceDetailSerializer,
    DataSourceCreateUpdateSerializer
)
from .data_provider import DataProvider


class DataSourceListCreateView(generics.ListCreateAPIView):
    """数据源列表/创建"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DataSourceCreateUpdateSerializer
        return DataSourceListSerializer
    
    def get_queryset(self):
        queryset = DataSource.objects.filter(created_by=self.request.user, is_active=True)
        
        # 搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # 类型过滤
        source_type = self.request.query_params.get('type')
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """重写 list 方法，返回统一格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 0,
                'message': 'success',
                'data': {
                    'results': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'page': self.paginator.page.number,
                    'page_size': self.paginator.page.paginator.per_page
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
    
    def perform_create(self, serializer):
        datasource = serializer.save(created_by=self.request.user)
        
        # 如果是文件类型，自动预览前10行
        if datasource.source_type in ['csv', 'json']:
            try:
                provider = DataProvider(datasource)
                preview_data = provider.get_preview(limit=10)
                datasource.preview_data = preview_data
                datasource.total_count = provider.get_total_count()
                datasource.save()
            except Exception as e:
                print(f"Error generating preview: {e}")
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        datasource = DataSource.objects.get(id=serializer.instance.id)
        detail_serializer = DataSourceDetailSerializer(datasource)
        
        return Response({
            'code': 0,
            'message': '创建成功',
            'data': detail_serializer.data
        }, status=status.HTTP_201_CREATED)


class DataSourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """数据源详情/更新/删除"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DataSourceCreateUpdateSerializer
        return DataSourceDetailSerializer
    
    def get_queryset(self):
        return DataSource.objects.filter(created_by=self.request.user, is_active=True)
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """上传数据文件"""
    if 'file' not in request.FILES:
        return Response({
            'code': 400,
            'message': '请上传文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    
    # 判断文件类型
    if file_name.endswith('.csv'):
        source_type = 'csv'
    elif file_name.endswith('.json'):
        source_type = 'json'
    else:
        return Response({
            'code': 400,
            'message': '不支持的文件类型，请上传 CSV 或 JSON 文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 解析文件
        if source_type == 'csv':
            content = uploaded_file.read().decode('utf-8')
            delimiter = request.data.get('delimiter', ',')
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
            data = list(reader)
        else:  # json
            content = uploaded_file.read().decode('utf-8')
            data = json.loads(content)
            if not isinstance(data, list):
                data = [data]
        
        # 限制预览数量
        preview_data = data[:10]
        total_count = len(data)
        
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'file_name': file_name,
                'source_type': source_type,
                'preview_data': preview_data,
                'total_count': total_count
            }
        })
    
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'文件解析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_connection(request, pk):
    """测试数据源连接"""
    datasource = get_object_or_404(
        DataSource,
        pk=pk,
        created_by=request.user,
        is_active=True
    )
    
    try:
        provider = DataProvider(datasource)
        success = provider.test_connection()
        
        if success:
            return Response({
                'code': 0,
                'message': '连接成功'
            })
        else:
            return Response({
                'code': 400,
                'message': '连接失败'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'连接失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_data(request, pk):
    """预览数据"""
    datasource = get_object_or_404(
        DataSource,
        pk=pk,
        created_by=request.user,
        is_active=True
    )
    
    limit = int(request.query_params.get('limit', 10))
    
    try:
        provider = DataProvider(datasource)
        data = provider.get_preview(limit=limit)
        total_count = provider.get_total_count()
        
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'preview': data,
                'total_count': total_count
            }
        })
    
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'获取数据失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data_by_index(request, pk):
    """获取指定索引的数据"""
    datasource = get_object_or_404(
        DataSource,
        pk=pk,
        created_by=request.user,
        is_active=True
    )
    
    index = int(request.query_params.get('index', 0))
    
    try:
        provider = DataProvider(datasource)
        data = provider.get_by_index(index)
        
        return Response({
            'code': 0,
            'message': 'success',
            'data': data
        })
    
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'获取数据失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_source_types(request):
    """获取数据源类型列表"""
    types = [
        {'value': 'csv', 'label': 'CSV文件', 'icon': 'Document'},
        {'value': 'json', 'label': 'JSON文件', 'icon': 'Document'},
        {'value': 'mysql', 'label': 'MySQL', 'icon': 'DataAnalysis'},
        {'value': 'postgresql', 'label': 'PostgreSQL', 'icon': 'DataAnalysis'},
        {'value': 'mongodb', 'label': 'MongoDB', 'icon': 'DataAnalysis'},
        {'value': 'redis', 'label': 'Redis', 'icon': 'Key'},
        {'value': 'python', 'label': 'Python脚本', 'icon': 'Code'},
    ]
    
    return Response({
        'code': 0,
        'message': 'success',
        'data': types
    })
