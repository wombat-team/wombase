from rest_framework import serializers
from .models import Tool, ToolCategory


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
    change_by = serializers.SerializerMethodField("get_change_by")
    category = serializers.SerializerMethodField("get_category")

    class Meta:
        model = Tool.history.model
        fields = (
            "name",
            "identifier",
            "category",
            "where_now",
            "status",
            "change_by",
            "changed_at",
        )

    def get_changed_at(self, tool):
        return tool.history_date.strftime("%d.%m.%Y %T")

    def get_where_now(self, tool_history):
        if tool_history.owner_full_name:
            return tool_history.owner_full_name
        if tool_history.currently_at:
            return tool_history.currently_at

    def get_status(self, tool):
        if tool.currently_at == Tool.DEFAULT_PLACE:
            return "returned"
        return "taken"

    def get_change_by(self, tool_history):
        return tool_history.change_by_full_name

    def get_category(self, tool_history):
        return tool_history.category_name
