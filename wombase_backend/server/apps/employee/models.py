from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from ..authentication.permissions import Permission


class Company(models.Model):
    name = models.CharField(max_length=30, unique=True)


class EmployeeRole(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name
