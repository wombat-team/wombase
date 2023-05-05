from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import empty

from ..core.models import Employee


class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'first_name', 'last_name', 'email', 'role', 'password')

    def create(self, validated_data):
        role = validated_data.pop('role')
        return Employee.objects.create_user(role_name=role.name, **validated_data)


class EmployeeLoginSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'password', 'token')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)
        self._errors = None
        self._validated_data = None

    def is_valid(self, *, raise_exception=False):
        phone_number = self.initial_data.get('phone_number')
        password = self.initial_data.get('password')
        errors = {}
        if not phone_number:
            errors['phone_number'] = 'This field is required'
        if not password:
            errors['password'] = 'This field is required'
        if errors:
            self._validated_data = {}
            self._errors = errors
            if raise_exception:
                raise serializers.ValidationError(errors)
            return False
        self._validated_data = dict(phone_number=phone_number, password=password)
        return True
