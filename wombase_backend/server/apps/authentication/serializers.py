from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'first_name', 'last_name', 'email', 'role', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        token = Token.objects.create(user=instance)
        return instance


class EmployeeLoginSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'password', 'token')
