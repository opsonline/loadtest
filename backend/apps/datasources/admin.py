from django.contrib import admin
from .models import DataSource


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'created_by', 'is_active', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
