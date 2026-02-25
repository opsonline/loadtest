from django.contrib import admin
from .models import Environment, Variable


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'environment', 'var_type', 'scope', 'is_active']
    list_filter = ['var_type', 'scope', 'is_active']
    search_fields = ['name']
