from rest_framework import serializers
from .models import Tool, ToolCategory
from ..core.models import Employee


class ToolListCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=ToolCategory.objects.all()
    )

    class Meta:
        model = Tool
        fields = (
            "id",
            "name",
            "identifier",
            "category",
            "description",
            "owner",
            "currently_at",
        )


class ToolPutDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=ToolCategory.objects.all()
    )

    class Meta:
        model = Tool
        fields = (
            "name",
            "identifier",
            "category",
            "description",
        )


class ToolDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=ToolCategory.objects.all()
    )

    class Meta:
        model = Tool
        fields = (
            "name",
            "identifier",
            "category",
            "description",
            "owner",
            "currently_at",
        )


class ToolCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolCategory
        fields = ("name", "description")


class ToolHistorySerializer(serializers.ModelSerializer):
    changed_at = serializers.SerializerMethodField("get_changed_at")
    where_now = serializers.SerializerMethodField("get_where_now")
    status = serializers.SerializerMethodField("get_status")
    changed_by = serializers.SerializerMethodField("get_changed_by")

    class Meta:
        model = Tool.history.model
        fields = (
            "name",
            "identifier",
            "category",
            "where_now",
            "status",
            "changed_by",
            "changed_at",
        )

    def get_changed_at(self, tool):
        return tool.history_date.strftime("%d.%m.%Y %T")

    def get_changed_by(self, tool):
        owner = Employee.objects.filter(id=tool.history_user_id).first()
        return owner.get_full_name()

    def get_where_now(self, tool):
        if tool.owner:
            return f"{tool.owner.first_name} {tool.owner.last_name}"
        if tool.currently_at:
            return tool.currently_at

    def get_status(self, tool):
        if tool.currently_at == Tool.DEFAULT_PLACE:
            return "returned"
        return "taken"
