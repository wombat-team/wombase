from rest_framework import generics, pagination
from .models import Tool, ToolCategory
from .serializers import ToolSerializer, ToolCategorySerializer

query_params = {
    'cat': 'category',
    'name': 'name',
    'own': 'owner'
}


class ToolListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ToolSerializer

    def get_queryset(self):
        queryset = Tool.objects.all()
        for query_param, param in query_params.items():
            if (value := self.request.query_params.get(*{query_param})) is not None:
                queryset = queryset.filter(
                     **{param: value} if param != "owner" else {"owner": f"+{value.strip()}"}
                )
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
