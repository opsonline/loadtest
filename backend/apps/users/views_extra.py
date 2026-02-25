from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .serializers import UserSerializer
from .permissions import IsAdminOrReadOnly


User = get_user_model()


class UserListView(generics.ListAPIView):
    """用户列表 - 仅管理员可访问"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        """支持搜索和过滤"""
        queryset = User.objects.all()
        
        # 搜索用户名或邮箱
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | Q(email__icontains=search)
            )
        
        # 按角色过滤
        role = self.request.query_params.get('role', '')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset.order_by('-created_at')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情 - 管理员可以修改所有用户，用户只能查看自己的信息"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        # 修改用户角色需要管理员权限
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_object(self):
        # 如果是获取自己的信息，则允许;如果是管理员，则可以获取任意用户
        pk = self.kwargs.get('pk')
        if pk == 'me' or str(pk) == str(self.request.user.pk):
            return self.request.user
        elif self.request.user.is_staff or self.request.user.role == 'admin':
            return super().get_object()
        else:
            # 普通用户不能查询其他用户
            return self.request.user


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, permissions.IsAdminUser])
def update_user_role(request, pk):
    """更新用户角色 - 仅管理员可操作"""
    user = get_object_or_404(User, pk=pk)
    
    role = request.data.get('role')
    if not role:
        return Response({
            'code': 400,
            'message': '角色不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if role not in ['admin', 'user', 'viewer']:
        return Response({
            'code': 400,
            'message': '无效的角色'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.role = role
    user.save()
    
    return Response({
        'code': 0,
        'message': '角色更新成功',
        'data': UserSerializer(user).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_permissions(request):
    """获取当前用户权限"""
    user = request.user
    permissions = {
        'is_admin': user.is_admin(),
        'is_viewer': user.is_viewer(),
        'can_manage_users': user.is_admin(),
        'can_create_scenarios': not user.is_viewer(),
        'can_run_tests': not user.is_viewer(),
        'can_delete_reports': user.is_admin() or user == request.user,
        'role': user.role
    }
    
    return Response({
        'code': 0,
        'message': 'success',
        'data': permissions
    })