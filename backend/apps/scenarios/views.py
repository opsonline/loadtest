import json
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Scenario, Request, HARImport
from .serializers import (
    ScenarioListSerializer, ScenarioDetailSerializer, 
    ScenarioCreateUpdateSerializer, RequestSerializer
)
from .har_parser import HARParser


class ScenarioListCreateView(generics.ListCreateAPIView):
    """场景列表/创建"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScenarioCreateUpdateSerializer
        return ScenarioListSerializer
    
    def get_queryset(self):
        queryset = Scenario.objects.filter(created_by=self.request.user, is_active=True)
        
        # 搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
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
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        scenario = Scenario.objects.get(id=serializer.instance.id)
        detail_serializer = ScenarioDetailSerializer(scenario)
        
        return Response({
            'code': 0,
            'message': '创建成功',
            'data': detail_serializer.data
        }, status=status.HTTP_201_CREATED)


class ScenarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """场景详情/更新/删除"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ScenarioCreateUpdateSerializer
        return ScenarioDetailSerializer
    
    def get_queryset(self):
        return Scenario.objects.filter(created_by=self.request.user, is_active=True)
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class ScenarioCopyView(generics.GenericAPIView):
    """复制场景"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        scenario = get_object_or_404(Scenario, pk=pk, created_by=request.user)
        
        # 复制场景
        new_scenario = Scenario.objects.create(
            name=f"{scenario.name} - 副本",
            description=scenario.description,
            created_by=request.user,
            default_users=scenario.default_users,
            default_spawn_rate=scenario.default_spawn_rate,
            default_duration=scenario.default_duration
        )
        
        # 复制请求
        for req in scenario.requests.filter(is_active=True):
            Request.objects.create(
                scenario=new_scenario,
                name=req.name,
                method=req.method,
                url=req.url,
                headers=req.headers,
                body_type=req.body_type,
                body=req.body,
                weight=req.weight,
                think_time=req.think_time,
                timeout=req.timeout,
                order=req.order
            )
        
        return Response({
            'code': 0,
            'message': '复制成功',
            'data': {'id': str(new_scenario.id)}
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_har(request):
    """导入 HAR 文件"""
    if 'file' not in request.FILES:
        return Response({
            'code': 400,
            'message': '请上传文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    har_file = request.FILES['file']
    scenario_name = request.data.get('name', har_file.name)
    resource_types = request.data.get('resource_types', 'xhr,document,other')
    host_replacement = request.data.get('host_replacement', '')
    
    try:
        # 解析 HAR 文件
        parser = HARParser()
        entries = parser.parse(har_file, resource_types.split(','))
        
        if not entries:
            return Response({
                'code': 400,
                'message': 'HAR 文件中没有找到可导入的请求'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建场景
        scenario = Scenario.objects.create(
            name=scenario_name,
            description=f"从 HAR 文件 {har_file.name} 导入",
            created_by=request.user,
            is_imported_from_har=True,
            har_file_name=har_file.name,
            default_users=10,
            default_spawn_rate=1,
            default_duration=60
        )
        
        # 创建请求
        for i, entry in enumerate(entries):
            url = entry['url']
            if host_replacement:
                url = parser.replace_host(url, host_replacement)
            
            Request.objects.create(
                scenario=scenario,
                name=f"请求 {i+1}",
                method=entry['method'],
                url=url,
                headers=entry.get('headers', {}),
                body_type=entry.get('body_type', 'none'),
                body=entry.get('body', ''),
                order=i
            )
        
        # 记录导入历史
        HARImport.objects.create(
            scenario=scenario,
            file_name=har_file.name,
            file_path=har_file.name,
            resource_types=resource_types.split(','),
            host_replacement=host_replacement or None,
            imported_count=len(entries)
        )
        
        return Response({
            'code': 0,
            'message': f'成功导入 {len(entries)} 个请求',
            'data': {
                'scenario_id': str(scenario.id),
                'imported_count': len(entries)
            }
        })
    
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'导入失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def scenario_stats(request, pk):
    """获取场景统计信息"""
    scenario = get_object_or_404(Scenario, pk=pk, created_by=request.user)
    
    stats = {
        'total_requests': scenario.requests.filter(is_active=True).count(),
        'total_reports': scenario.reports.count(),
        'last_run': scenario.reports.filter(status='completed').order_by('-created_at').first()
    }
    
    if stats['last_run']:
        stats['last_run'] = {
            'id': str(stats['last_run'].id),
            'created_at': stats['last_run'].created_at,
            'status': stats['last_run'].status
        }
    
    return Response({
        'code': 0,
        'message': 'success',
        'data': stats
    })
