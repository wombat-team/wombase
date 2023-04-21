from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=30, unique=True)


class EmployeeRole(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.name
