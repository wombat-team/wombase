from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response

from ..core.models import Employee, EmployeeRole
from .serializers import EmployeeDetailsSerializer, EmployeeListCreateSerializer, EmployeeRoleSerializer


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeListCreateSerializer


class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeDetailsSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            for key, value in serializer.validated_data.items():
                setattr(instance, key, value)
            instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeRoleViewSet(viewsets.ModelViewSet):
    queryset = EmployeeRole.objects.all()
    serializer_class = EmployeeRoleSerializer

    def update(self, request, *args, **kwargs):
        return Response({'message': 'PUT method is not available'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
