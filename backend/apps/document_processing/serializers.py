
from rest_framework import serializers

from .models import OCRJob


class OCRJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OCRJob
        fields = ("language",)

    def validate_language(self, value):
        supported_languages = {"fas", "eng", "fas+eng"}

        if value not in supported_languages:
            raise serializers.ValidationError(
                "Supported languages are fas, eng and fas+eng."
            )

        return value


class OCRJobSerializer(serializers.ModelSerializer):
    resource_file_id = serializers.IntegerField(
        source="resource_file.id",
        read_only=True,
    )

    class Meta:
        model = OCRJob
        fields = (
            "id",
            "resource_file_id",
            "status",
            "language",
            "extracted_text",
            "error_message",
            "created_at",
            "started_at",
            "completed_at",
        )
        read_only_fields = fields
