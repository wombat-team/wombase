from rest_framework import serializers
from .models import Tool, ToolCategory


class ToolSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", queryset=ToolCategory.objects.all())

    class Meta:
        model = Tool
        fields = (
            "identifier",
            "name",
            "description",
            "category",
            "owner"
        )


class ToolCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolCategory
        fields = (
            "name",
            "description"
        )
