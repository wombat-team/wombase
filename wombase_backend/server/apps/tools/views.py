from rest_framework import generics, status
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .models import Tool, ToolCategory
from .serializers import (
    ToolListCreateSerializer,
    ToolDetailSerializer,
    ToolCategorySerializer,
    ToolHistorySerializer,
    ToolPutDetailSerializer,
)
from ..authentication.permissions import (
    PermissionViewMixin,
    UNSAFE_METHODS,
    ViewCategoriesPermission,
    UpdateCategoriesPermission,
    ToolTransferPermission,
    ViewToolHistoryPermission,
    UpdateToolHistoryPermission,
)


class ToolListCreateAPIView(PermissionViewMixin, generics.ListCreateAPIView):
    serializer_class = ToolListCreateSerializer

    def get_queryset(self):
        queryset = Tool.objects.all()
        for query_param, param_value in self.request.query_params.items():
            if query_param == "category":
                queryset = queryset.filter(category__name__icontains=param_value)
            else:
                queryset = queryset.filter(**{f"{query_param}__icontains": param_value})
        return queryset


class ToolRetrieveUpdateDestroyAPIView(PermissionViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolDetailSerializer

    def put(self, request, *args, **kwargs):
        tool = self.get_object()
        tool_serializer = ToolPutDetailSerializer(
            tool,
            data=request.data,
        )
        if tool_serializer.is_valid():
            tool.skip_history_when_saving = True
            tool_serializer.save()
            return Response(tool_serializer.data)
        return Response(tool_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToolCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = ToolCategory.objects.all()
    serializer_class = ToolCategorySerializer

    def get_permissions(self):
        method = self.request.method
        print(method)
        if method in SAFE_METHODS:
            permission_classes = [ViewCategoriesPermission]
        elif method in UNSAFE_METHODS:
            permission_classes = [UpdateCategoriesPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ToolCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ToolCategory.objects.all()
    serializer_class = ToolCategorySerializer

    def get_permissions(self):
        method = self.request.method
        print(method)
        if method in SAFE_METHODS:
            permission_classes = [ViewCategoriesPermission]
        elif method in UNSAFE_METHODS:
            permission_classes = [UpdateCategoriesPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ToolTransferAPIView(generics.UpdateAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolDetailSerializer
    permission_classes = (ToolTransferPermission,)

    def patch(self, request, *args, **kwargs):
        tool = self.get_object()
        data = request.data
        request_owner = data.get("owner")
        request_currently_at = data.get("currently_at")
        if request_owner and request_currently_at:
            return Response(
                {
                    "detail": "The owner and currently_at fields cannot both have a value. "
                    "Please provide a value for only one of them."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request_owner is None and request_currently_at is None:
            return Response(
                {
                    "detail": "Both owner and currently_at fields are empty. "
                    "Please provide a value for either one of them."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request_owner:
            if tool.owner and str(tool.owner.id) == request_owner:
                return Response(
                    {
                        "detail": "The tool cannot be transferred to the same owner."
                        "Please provide value of another new owner or mew location."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tool_serializer = ToolDetailSerializer(
                tool,
                data={"owner": request_owner, "currently_at": None},
                partial=True,
            )

        if request_currently_at:
            if tool.currently_at == request_currently_at:
                return Response(
                    {
                        "detail": "The tool cannot be transferred to the same location."
                        "Please provide value of another new owner or mew location."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tool_serializer = ToolDetailSerializer(
                tool,
                data={"owner": None, "currently_at": request_currently_at},
                partial=True,
            )

        if tool_serializer.is_valid():
            tool_serializer.save()
            return Response(tool_serializer.data)
        return Response(tool_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToolChangesHistoryAPIView(generics.ListAPIView):
    serializer_class = ToolHistorySerializer

    def get_queryset(self):
        queryset = Tool.history.filter(history_type="~")
        for query_param, param_value in self.request.query_params.items():
            queryset = queryset.filter(**{f"{query_param}__icontains": param_value})
        return queryset

    def get_permissions(self):
        method = self.request.method
        print(method)
        if method in SAFE_METHODS:
            permission_classes = [ViewToolHistoryPermission]
        elif method in UNSAFE_METHODS:
            permission_classes = [UpdateToolHistoryPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
