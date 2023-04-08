from rest_framework import generics, pagination
from .models import Tool, ToolCategory
from .serializers import ToolSerializer, ToolCategorySerializer


class ToolListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ToolSerializer

    def get_queryset(self):
        queryset = Tool.objects.all()

        if (category := self.request.query_params.get("cat")) is not None:
            queryset = queryset.filter(category=category)

        if (name := self.request.query_params.get("name")) is not None:
            queryset = queryset.filter(name=name)

        if (identifier := self.request.query_params.get("id")) is not None:
            queryset = queryset.filter(identifier=identifier)

        if (owner := self.request.query_params.get("own")) is not None:
            queryset = queryset.filter(owner=owner)

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

