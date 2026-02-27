from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Environment, Variable
from .serializers import (
    EnvironmentListSerializer,
    EnvironmentDetailSerializer,
    EnvironmentCreateUpdateSerializer,
    VariableSerializer,
)


class EnvironmentListCreateView(generics.ListCreateAPIView):
    """环境列表/创建"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EnvironmentCreateUpdateSerializer
        return EnvironmentListSerializer

    def get_queryset(self):
        queryset = Environment.objects.filter(
            created_by=self.request.user, is_active=True
        )

        # 搜索
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        # 如果设置为默认环境，取消其他默认环境
        if serializer.validated_data.get("is_default"):
            Environment.objects.filter(
                created_by=self.request.user, is_default=True
            ).update(is_default=False)

        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "code": 0,
                    "message": "success",
                    "data": {
                        "results": serializer.data,
                        "count": self.paginator.page.paginator.count,
                        "page": self.paginator.page.number,
                        "page_size": self.paginator.page.paginator.per_page,
                    },
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {"results": serializer.data, "count": len(serializer.data)},
            }
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        environment = Environment.objects.get(id=serializer.instance.id)
        detail_serializer = EnvironmentDetailSerializer(environment)

        return Response(
            {"code": 0, "message": "创建成功", "data": detail_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class EnvironmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """环境详情/更新/删除"""

    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return EnvironmentCreateUpdateSerializer
        return EnvironmentDetailSerializer

    def get_queryset(self):
        return Environment.objects.filter(created_by=self.request.user, is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 0, "message": "success", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        detail_serializer = EnvironmentDetailSerializer(instance)
        return Response(
            {"code": 0, "message": "更新成功", "data": detail_serializer.data}
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return Response({"code": 0, "message": "删除成功"})


class VariableListCreateView(generics.ListCreateAPIView):
    """变量列表/创建"""

    serializer_class = VariableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        environment_id = self.kwargs.get("environment_id")
        return Variable.objects.filter(
            environment_id=environment_id,
            environment__created_by=self.request.user,
            is_active=True,
        )

    def perform_create(self, serializer):
        environment = get_object_or_404(
            Environment,
            pk=self.kwargs.get("environment_id"),
            created_by=self.request.user,
        )
        serializer.save(environment=environment)


class VariableDetailView(generics.RetrieveUpdateDestroyAPIView):
    """变量详情/更新/删除"""

    serializer_class = VariableSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return Variable.objects.filter(
            environment__created_by=self.request.user, is_active=True
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_default_environment(request):
    """获取默认环境"""
    environment = Environment.objects.filter(
        created_by=request.user, is_default=True, is_active=True
    ).first()

    if not environment:
        # 如果没有默认环境，返回第一个环境
        environment = Environment.objects.filter(
            created_by=request.user, is_active=True
        ).first()

    if environment:
        serializer = EnvironmentDetailSerializer(environment)
        return Response({"code": 0, "message": "success", "data": serializer.data})

    return Response(
        {"code": 404, "message": "未找到环境配置"}, status=status.HTTP_404_NOT_FOUND
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_default_environment(request, pk):
    """设置默认环境"""
    environment = get_object_or_404(
        Environment, pk=pk, created_by=request.user, is_active=True
    )

    # 取消其他默认环境
    Environment.objects.filter(created_by=request.user, is_default=True).update(
        is_default=False
    )

    # 设置当前环境为默认
    environment.is_default = True
    environment.save()

    return Response({"code": 0, "message": "设置成功"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def preview_variables(request, pk):
    """预览变量替换效果"""
    environment = get_object_or_404(
        Environment, pk=pk, created_by=request.user, is_active=True
    )

    test_text = request.data.get("text", "")
    variables = environment.variables.filter(is_active=True)

    # 替换变量
    preview_text = test_text
    for var in variables:
        placeholder = f"${{{var.name}}}"
        preview_text = preview_text.replace(placeholder, var.value)

    return Response(
        {
            "code": 0,
            "message": "success",
            "data": {"original": test_text, "preview": preview_text},
        }
    )
