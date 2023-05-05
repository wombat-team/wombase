from django.urls import path
from .views import (
    ToolListCreateAPIView,
    ToolRetrieveUpdateDestroyAPIView,
    ToolCategoryListCreateAPIView,
    ToolCategoryRetrieveUpdateDestroyAPIView,
    ToolTransferAPIView,
    ToolChangesHistoryAPIView,
)

urlpatterns = [
    path("", ToolListCreateAPIView.as_view()),
    path("<pk>", ToolRetrieveUpdateDestroyAPIView.as_view()),
    path("category/", ToolCategoryListCreateAPIView.as_view()),
    path("category/<pk>", ToolCategoryRetrieveUpdateDestroyAPIView.as_view()),
    path("transfer/<pk>", ToolTransferAPIView.as_view()),
    path("history/", ToolChangesHistoryAPIView.as_view()),
]
