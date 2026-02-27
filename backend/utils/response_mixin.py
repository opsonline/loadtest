from rest_framework.response import Response
from rest_framework import status


class UnifiedResponseMixin:
    """统一响应格式的Mixin"""

    def list(self, request, *args, **kwargs):
        """重写 list 方法"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self._paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self._success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """重写 retrieve 方法"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self._success_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """重写 create 方法"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        detail_serializer = self.get_serializer(serializer.instance)
        return self._success_response(
            detail_serializer.data,
            message="创建成功",
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        """重写 update 方法"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        detail_serializer = self.get_serializer(instance)
        return self._success_response(detail_serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        """重写 destroy 方法"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return self._success_response(None, message="删除成功")

    def _success_response(
        self, data=None, message="success", status=status.HTTP_200_OK, headers=None
    ):
        """成功响应"""
        response_data = {"code": 0, "message": message, "data": data}
        return Response(response_data, status=status, headers=headers)

    def _paginated_response(self, data):
        """分页响应"""
        paginator = self.paginator.page.paginator
        return self._success_response(
            {
                "results": data,
                "count": paginator.count,
                "page": self.paginator.page.number,
                "page_size": paginator.per_page,
            }
        )
