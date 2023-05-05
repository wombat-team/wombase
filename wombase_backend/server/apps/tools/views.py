from datetime import datetime
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Tool, ToolCategory
from .serializers import (
    ToolListCreateSerializer,
    ToolDetailSerializer,
    ToolCategorySerializer,
    ToolHistorySerializer,
    ToolPutDetailSerializer,
)


class ToolListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ToolListCreateSerializer

    def get_queryset(self):
        queryset = Tool.objects.all()
        for query_param, param_value in self.request.query_params.items():
            if query_param == "name":
                queryset = queryset.filter(name__icontains=param_value)
            if query_param == "category":
                queryset = queryset.filter(category__name__icontains=param_value)
            if query_param == "identifier":
                queryset = queryset.filter(identifier__icontains=param_value)
            if query_param == "currently_at":
                queryset = queryset.filter(currently_at__icontains=param_value)
        return queryset


class ToolRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
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


class ToolCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ToolCategory.objects.all()
    serializer_class = ToolCategorySerializer


class ToolTransferAPIView(generics.UpdateAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolDetailSerializer

    def patch(self, request, *args, **kwargs):
        tool = self.get_object()
        data = request.data
        owner = data.get("owner")
        currently_at = data.get("currently_at")
        if owner is not None and currently_at is not None:
            return Response(
                {
                    "detail": "The owner and currently_at fields cannot both have a value. "
                    "Please provide a value for only one of them."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if owner is None and currently_at is None:
            return Response(
                {
                    "detail": "Both owner and currently_at fields are empty. "
                    "Please provide a value for either one of them."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if owner is not None:
            if tool.owner is not None and str(tool.owner.id) == owner:
                return Response(
                    {
                        "detail": "The tool cannot be transferred to the same owner."
                        "Please provide value of another new owner or mew location."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tool_serializer = ToolDetailSerializer(
                tool,
                data={"owner": owner, "currently_at": None},
                partial=True,
            )

        if currently_at is not None:
            if tool.currently_at == currently_at:
                return Response(
                    {
                        "detail": "The tool cannot be transferred to the same location."
                        "Please provide value of another new owner or mew location."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tool_serializer = ToolDetailSerializer(
                tool,
                data={"owner": None, "currently_at": currently_at},
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
            if query_param == "name":
                queryset = queryset.filter(name__icontains=param_value)
            if query_param == "category":
                queryset = queryset.filter(category__name__icontains=param_value)
            if query_param == "identifier":
                queryset = queryset.filter(identifier__icontains=param_value)
            if query_param == "owner":
                queryset = queryset.filter(owner__id__icontains=param_value)
            if query_param == "currently_at":
                queryset = queryset.filter(currently_at__icontains=param_value)
        return queryset
