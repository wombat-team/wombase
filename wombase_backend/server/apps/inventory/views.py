from rest_framework import generics, status
from rest_framework.response import Response

from .models import Tool, ToolCategory
from ..staff.models import Employee
from .serializers import ToolSerializer, ToolCategorySerializer


class ToolListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ToolSerializer

    def get_queryset(self):
        queryset = Tool.objects.all()
        for query_param, param_value in self.request.query_params.items():
            if param_value is not None:
                queryset = queryset.filter(**{query_param: param_value})
        return queryset


class ToolRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer


class ToolCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = ToolCategory.objects.all()
    serializer_class = ToolCategorySerializer


class ToolCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ToolCategory.objects.all()
    serializer_class = ToolCategorySerializer
