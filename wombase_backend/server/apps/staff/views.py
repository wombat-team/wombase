from rest_framework import generics, status, viewsets
from rest_framework.response import Response

from .models import Employee, EmployeeRole
from .serializers import EmployeeDetailsSerializer, EmployeeListCreateSerializer, EmployeeRoleSerializer


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeListCreateSerializer


class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeDetailsSerializer

    def patch(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = Employee.objects.get(id=user_id)

        phone_number = request.data.get('phone_number', user.phone_number)
        first_name = request.data.get('first_name', user.first_name)
        last_name = request.data.get('last_name', user.last_name)
        email = request.data.get('email', user.email)
        new_password = request.data.get('new_password')

        user.phone_number = phone_number
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if new_password:
            user.set_password(new_password)

        user.save()

        return Response(EmployeeDetailsSerializer(user).data, status=status.HTTP_200_OK)


class EmployeeRoleViewSet(viewsets.ModelViewSet):
    queryset = EmployeeRole.objects.all()
    serializer_class = EmployeeRoleSerializer

    def update(self, request, *args, **kwargs):
        return Response({'message': 'PUT method is not available'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
