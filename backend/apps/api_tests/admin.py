from django.contrib import admin
from .models import TestSuite, TestCase, Assertion, TestResult


@admin.register(TestSuite)
class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'suite', 'method', 'url', 'is_active', 'order']
    list_filter = ['method', 'is_active']
    search_fields = ['name', 'url']


@admin.register(Assertion)
class AssertionAdmin(admin.ModelAdmin):
    list_display = ['name', 'test_case', 'assertion_type', 'is_active']
    list_filter = ['assertion_type', 'is_active']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_case', 'status', 'response_status', 'response_time', 'created_at']
    list_filter = ['status', 'created_at']
