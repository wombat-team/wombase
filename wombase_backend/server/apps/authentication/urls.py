from django.urls import path

from .views import EmployeeRegistrationAPIView, EmployeeLoginAPIView

urlpatterns = [
    path('register/', EmployeeRegistrationAPIView.as_view()),
    path('login/', EmployeeLoginAPIView.as_view()),
]
