from django.urls import path
from .views import ToolListCreateAPIView, ToolRetrieveUpdateDestroyAPIView, ToolCategoryListCreateAPIView, ToolCategoryRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('tools/', ToolListCreateAPIView.as_view()),
    path('tools/<pk>', ToolRetrieveUpdateDestroyAPIView.as_view()),
    path('tools/category/', ToolCategoryListCreateAPIView.as_view()),
    path('tools/category/<pk>', ToolCategoryRetrieveUpdateDestroyAPIView.as_view())
]
