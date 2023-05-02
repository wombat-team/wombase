from django.db import models
from simple_history.models import HistoricalRecords

from ..core.models import Employee


class ToolCategory(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Tool(models.Model):
    DEFAULT_PLACE = "warehouse"

    identifier = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(ToolCategory, on_delete=models.CASCADE)
    owner = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True)
    currently_at = models.CharField(max_length=20, default=DEFAULT_PLACE, null=True)

    history = HistoricalRecords(user_related_name="changed_by")

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return self.name
