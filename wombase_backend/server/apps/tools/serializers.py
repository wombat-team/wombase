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
