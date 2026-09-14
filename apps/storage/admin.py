from django.contrib import admin

from .models import StoredFile


@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "original_name",
        "owner",
        "file_size",
        "uploaded_at",
    )

    list_filter = ("uploaded_at",)

    search_fields = (
        "original_name",
        "owner__email",
    )