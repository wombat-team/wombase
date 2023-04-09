from django.urls import path

from .views import EmployeeRetrieveUpdateDestroyAPIView, EmployeeListCreateAPIView

urlpatterns = [
    path('<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view()),
    path('', EmployeeListCreateAPIView.as_view()),
]