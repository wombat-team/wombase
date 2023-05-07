from django.db import models
from django.dispatch import receiver
from simple_history.models import HistoricalRecords
from simple_history.signals import pre_create_historical_record

from ..core.models import Employee


class ToolCategory(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name


class FullName(models.Model):
    owner_full_name = models.CharField(max_length=50, null=True)
    change_by_full_name = models.CharField(max_length=50)
    category_name = models.CharField(max_length=20)

    class Meta:
        abstract = True


class Tool(models.Model):
    DEFAULT_PLACE = "warehouse"

    identifier = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    category = models.ForeignKey(ToolCategory, on_delete=models.CASCADE)
    owner = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True)
    currently_at = models.CharField(max_length=20, default=DEFAULT_PLACE, null=True)

    history = HistoricalRecords(
        user_related_name="changed_by",
        excluded_fields=(
            "description",
            "owner",
            "category",
        ),
        bases=(FullName,),
    )

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return self.name

    @receiver(pre_create_historical_record)
    def pre_create_historical_record_callback(sender, **kwargs):
        history_instance = kwargs["history_instance"]
        source_instance = kwargs["instance"]
        if source_instance.owner:
            history_instance.owner_full_name = source_instance.owner.get_full_name()
        else:
            history_instance.owner_full_name = None
        history_instance.change_by_full_name = Employee.objects.get(
            id=history_instance.history_user_id
        ).get_full_name()
        history_instance.category_name = source_instance.category.name
