from rest_framework import serializers

from ..models import StoredFile


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = [
            "id",
            "file",
            "original_name",
            "file_size",
            "uploaded_at",
        ]

        read_only_fields = [
            "id",
            "original_name",
            "file_size",
            "uploaded_at",
        ]


class FileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = [
            "id",
            "original_name",
            "file_size",
            "uploaded_at",
        ]
    


class FileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = [
            "id",
            "original_name",
            "file_size",
            "file",
            "uploaded_at",
        ]