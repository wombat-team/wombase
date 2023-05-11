from django.db import models
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated

UNSAFE_METHODS = ["POST", "PUT", "DELETE", "PATCH"]


class Permission(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class BaseCustomPermission(BasePermission):
    required_permissions = []

    def has_permission(self, request, view):
        is_auth = request.user.is_authenticated
        permissions = request.user.role.permissions
        has_perm = permissions.filter(name__in=self.required_permissions).exists()
        return is_auth and has_perm


class ReadPermission(BaseCustomPermission):
    required_permissions = ['view_employee', 'view_tools']


class UpdatePermission(BaseCustomPermission):
    required_permissions = ['update_employee', 'update_tools']


class ViewRolesPermission(BaseCustomPermission):
    required_permissions = ['view_employee_roles']


class UpdateRolesPermission(BaseCustomPermission):
    required_permissions = ['update_employee_roles']


class ViewToolHistoryPermission(BaseCustomPermission):
    required_permissions = ['view_inventory_log']


class UpdateToolHistoryPermission(BaseCustomPermission):
    required_permissions = ['update_inventory_log']


class ViewCategoriesPermission(BaseCustomPermission):
    required_permissions = ['view_tools_categories']


class UpdateCategoriesPermission(BaseCustomPermission):
    required_permissions = ['update_tools_categories']


class ToolTransferPermission(BasePermission):
    required_permissions = ['take_tool', 'return_tool']

    def has_permission(self, request, view):
        is_auth = request.user.is_authenticated
        permissions = request.user.role.permissions
        has_perm = all(permissions.filter(name=permission).exists() for permission in self.required_permissions)
        return is_auth and has_perm


class PermissionViewMixin:
    def get_permissions(self):
        method = self.request.method
        print(method)
        if method in SAFE_METHODS:
            permission_classes = [ReadPermission]
        elif method in UNSAFE_METHODS:
            permission_classes = [UpdatePermission]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
