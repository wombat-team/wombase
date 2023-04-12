from django.urls import path, include
from rest_framework import routers

from .views import EmployeeRetrieveUpdateDestroyAPIView, EmployeeListCreateAPIView, EmployeeRoleViewSet

router = routers.DefaultRouter()
router.register(r'roles', EmployeeRoleViewSet)

urlpatterns = [
    path('<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view()),
    path('', EmployeeListCreateAPIView.as_view()),
    path('', include(router.urls)),
]
