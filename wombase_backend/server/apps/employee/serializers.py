from rest_framework import serializers

from ..authentication.permissions import Permission
from ..core.models import Employee
from .models import EmployeeRole


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, write_only=True, required=False)

    class Meta:
        model = Employee
        fields = ('phone_number', 'first_name', 'last_name', 'password', 'email', 'role')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class EmployeeListCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, write_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'password', 'email', 'role')

class EmployeeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRole
        fields = ('name', 'permissions')


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name')
