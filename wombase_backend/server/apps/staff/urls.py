from django.urls import path, include

from .views import EmployeeListAPIView, EmployeeRetrieveUpdateDestroyAPIView, EmployeeListCreateAPIView

urlpatterns = [
    path('list', EmployeeListAPIView.as_view()),
    path('<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view()),
    path('new', EmployeeListCreateAPIView.as_view()),
]