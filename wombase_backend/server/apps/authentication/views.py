from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .serializers import EmployeeRegistrationSerializer, EmployeeLoginSerializer


class EmployeeRegistrationView(CreateAPIView):
    serializer_class = EmployeeRegistrationSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(serializer.data)


class EmployeeLoginView(CreateAPIView):
    serializer_class = EmployeeLoginSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        phone_number = serializer.initial_data.get('phone_number')
        password = serializer.initial_data.get('password')

        user = authenticate(phone_number=phone_number, password=password)
        if user is not None:
            token = Token.objects.get(user=user)
            return Response({'token': token.key})
        else:
            return Response({'detail': 'Invalid phone number or password'}, status=status.HTTP_400_BAD_REQUEST)
