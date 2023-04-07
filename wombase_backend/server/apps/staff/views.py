from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Employee
from .serializers import EmployeeSerializer

# Create your views here.
class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def perform_create(self, serializer):
        serializer.save()

class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            return Employee.objects.get(pk=pk)
        except Employee is None:
            raise NotFound(detail="Object not found you")

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)