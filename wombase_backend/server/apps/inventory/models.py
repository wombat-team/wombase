from django.db import models

from ..staff.models import Employee


class ToolCategory(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name



class Tool(models.Model):
    identifier = models.CharField(max_length=15, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(ToolCategory, on_delete=models.CASCADE)
    owner = models.ForeignKey(Employee, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
