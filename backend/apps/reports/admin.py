from django.contrib import admin
from .models import Report, RequestStats


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario', 'status', 'users', 'duration', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']


@admin.register(RequestStats)
class RequestStatsAdmin(admin.ModelAdmin):
    list_display = ['report', 'request_name', 'num_requests', 'avg_response_time', 'created_at']
    search_fields = ['request_name']
