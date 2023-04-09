from django.urls import path, include

from .views import EmployeeRetrieveUpdateDestroyAPIView, EmployeeListCreateAPIView

urlpatterns = [
    path('<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view()),
    path('list', EmployeeListCreateAPIView.as_view()),
]