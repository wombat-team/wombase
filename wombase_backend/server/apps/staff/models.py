from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=30, unique=True)


class EmployeeRole(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.name


class EmployeeManager(BaseUserManager):
    def create_user(
            self,
            phone_number: str,
            password: str,
            role_name: str,
            first_name: str,
            last_name: str,
            email: str = None
    ):
        role = EmployeeRole.objects.get(name=role_name)
        employee = self.model(
            phone_number=phone_number,
            role=role,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_staff=False,
            is_superuser=False
        )
        employee.set_password(password)
        employee.save()
        return employee

    def create_superuser(self, phone_number: str, password: str, **kwargs):
        admin = self.model(
            phone_number=phone_number,
            is_staff=True,
            is_superuser=True,
            **kwargs
        )
        admin.set_password(password)
        admin.save()
        return admin


class Employee(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True, primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True, unique=True)
    role = models.ForeignKey(EmployeeRole, on_delete=models.SET_NULL, null=True)
    objects = EmployeeManager()
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if not self.is_superuser else f'Admin {self.phone_number}'
