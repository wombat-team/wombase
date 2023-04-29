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
    changed_at = serializers.SerializerMethodField('get_changed_at')
    where_now = serializers.SerializerMethodField('get_where_now')
    status = serializers.SerializerMethodField('get_status')
    changed_by = serializers.SerializerMethodField('get_changed_by')

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

    def get_changed_at(self, obj):
        return obj.history_date.strftime("%d.%m.%Y %T")

    def get_changed_by(self, obj):
        return obj.history_user_id

    def get_where_now(self, obj):
        if obj.owner:
            return obj.owner.first_name + " " + obj.owner.last_name
        if obj.currently_at:
            return obj.currently_at

    def get_status(self, obj):
        if obj.currently_at == Tool.DEFAULT_PLACE:
            return 'returned'
        if obj.currently_at or obj.owner:
            return 'taken'
