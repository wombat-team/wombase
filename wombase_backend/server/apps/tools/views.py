from rest_framework import generics, status
from rest_framework.response import Response

from .models import Tool, ToolCategory
from .serializers import ToolSerializer, ToolCategorySerializer


class ToolListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ToolSerializer

    def get_queryset(self):
        queryset = Tool.objects.all()
        for query_param, param_value in self.request.query_params.items():
            if param_value is not None:
                if query_param == 'name':
                    queryset = queryset.filter(name__icontains=param_value)
                if query_param == 'category':
                    queryset = queryset.filter(category__name__icontains=param_value)
                if query_param == 'available':
                    queryset = queryset.filter(currently_at=Tool.DEFAULT_PLACE)
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


class ToolTransferAPIView(generics.UpdateAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer

    def patch(self, request, *args, **kwargs):
        tool = self.get_object()
        data = request.data
        if data.get("currently_at") is None:
            tool_serializer = ToolSerializer(
                tool, data={"owner": data.get("owner"), "currently_at": None}, partial=True
            )
        else:
            tool_serializer = ToolSerializer(
                tool,
                data={"owner": None, "currently_at": data.get("currently_at")},
                partial=True,
            )
        if tool_serializer.is_valid():
            tool_serializer.save()
            return Response(tool_serializer.data)
        return Response(tool_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToolReturnAPIView(generics.UpdateAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer

    def patch(self, request, *args, **kwargs):
        tool = self.get_object()
        tool_serializer = ToolSerializer(
            tool, data={"owner": None, "currently_at": Tool.DEFAULT_PLACE}, partial=True
        )
        if tool_serializer.is_valid():
            tool_serializer.save()
            return Response(tool_serializer.data)
        return Response(tool_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
