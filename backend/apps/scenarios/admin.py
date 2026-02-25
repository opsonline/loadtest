from django.contrib import admin
from .models import Scenario, Request, HARImport


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_imported_from_har', 'is_active', 'created_at']
    list_filter = ['is_imported_from_har', 'is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario', 'method', 'url', 'is_active', 'order']
    list_filter = ['method', 'is_active']
    search_fields = ['name', 'url']


@admin.register(HARImport)
class HARImportAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'scenario', 'imported_count', 'created_at']
    search_fields = ['file_name']
