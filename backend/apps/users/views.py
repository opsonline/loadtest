from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer
from .authentication import generate_token


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """获取仪表盘统计数据"""
    from apps.scenarios.models import Scenario
    from apps.reports.models import Report
    from apps.datasources.models import DataSource
    from apps.api_tests.models import TestSuite
    
    # 获取当前用户的统计数据
    stats = {
        'scenario_count': Scenario.objects.filter(created_by=request.user, is_active=True).count(),
        'report_count': Report.objects.filter(created_by=request.user).count(),
        'datasource_count': DataSource.objects.filter(created_by=request.user).count(),
        'test_suite_count': TestSuite.objects.filter(created_by=request.user).count(),
    }
    
    # 获取最近5条报告
    recent_reports = Report.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    recent_reports_data = []
    for report in recent_reports:
        recent_reports_data.append({
            'id': str(report.id),
            'name': report.name,
            'scenario_name': report.scenario.name if report.scenario else '',
            'status': report.status,
            'created_at': report.created_at.isoformat() if report.created_at else None,
        })
    
    return Response({
        'code': 0,
        'message': 'success',
        'data': {
            'stats': stats,
            'recent_reports': recent_reports_data
        }
    })


class UserRegisterView(generics.CreateAPIView):
    """用户注册"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 生成token
        tokens = generate_token(user)
        
        return Response({
            'code': 0,
            'message': '注册成功',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录"""
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({
            'code': 4001,
            'message': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    tokens = generate_token(user)
    
    return Response({
        'code': 0,
        'message': '登录成功',
        'data': {
            'user': UserSerializer(user).data,
            'tokens': tokens
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """获取用户信息"""
    return Response({
        'code': 0,
        'message': 'success',
        'data': UserSerializer(request.user).data
    })
