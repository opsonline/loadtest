from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理员用户拥有全部权限，普通用户只有只读权限
    """

    def has_permission(self, request, view):
        # 对于只读请求（GET, HEAD, OPTIONS），任何已认证的用户都可以访问
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 其他操作需要是管理员
        return request.user.is_authenticated and request.user.is_admin()