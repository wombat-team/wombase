from django.contrib import admin

from .models import EmployeeRole, Company
from ..core.models import Employee

admin.site.register([Employee, EmployeeRole, Company])
