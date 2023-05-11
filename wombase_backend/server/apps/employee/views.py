from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from ..authentication.permissions import (
    ViewRolesPermission,
    UpdateRolesPermission,
    UNSAFE_METHODS,
    Permission,
    PermissionViewMixin,
)
from ..core.models import Employee, EmployeeRole
from .serializers import (
    EmployeeDetailsSerializer,
    EmployeeListCreateSerializer,
    EmployeeRoleSerializer,
    PermissionSerializer,
)


class EmployeeListCreateAPIView(PermissionViewMixin, generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeListCreateSerializer


class EmployeeRetrieveUpdateDestroyAPIView(PermissionViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeDetailsSerializer


class EmployeeRoleViewSet(viewsets.ModelViewSet):
    queryset = EmployeeRole.objects.all()
    serializer_class = EmployeeRoleSerializer

    def update(self, request, *args, **kwargs):
        return Response({'message': 'PUT method is not available'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        method = self.request.method
        if method in SAFE_METHODS:
            permission_classes = [ViewRolesPermission]
        elif method in UNSAFE_METHODS:
            permission_classes = [UpdateRolesPermission]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class PermissionsListCreateAPIView(generics.ListCreateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = ()


class PermissionsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = ()