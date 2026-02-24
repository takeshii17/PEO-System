from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("document_name", "division", "status", "doc_type", "created_at")
    list_filter = ("division", "status", "doc_type")
    search_fields = ("document_name", "description", "billing_type")
