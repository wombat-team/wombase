from rest_framework import serializers

from .models import Employee, EmployeeRole


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, write_only=True)

    class Meta:
        model = Employee
        fields = ('phone_number', 'first_name', 'last_name', 'password', 'email', 'role')


class EmployeeListCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, write_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'password', 'email', 'role')


class EmployeeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRole
        fields = ('name',)
