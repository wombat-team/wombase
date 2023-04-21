from django.urls import path
from .views import (ToolListCreateAPIView, ToolRetrieveUpdateDestroyAPIView,
                    ToolCategoryListCreateAPIView, ToolCategoryRetrieveUpdateDestroyAPIView,
                    ToolTransferAPIView, ToolReturnAPIView)
urlpatterns = [
    path('tools/', ToolListCreateAPIView.as_view()),
    path('tools/<pk>', ToolRetrieveUpdateDestroyAPIView.as_view()),
    path('tools/category/', ToolCategoryListCreateAPIView.as_view()),
    path('tools/category/<pk>', ToolCategoryRetrieveUpdateDestroyAPIView.as_view()),

    path('tools/transfer/<pk>', ToolTransferAPIView.as_view()),
    path('tools/return/<pk>', ToolReturnAPIView.as_view()),
]