from django.apps import AppConfig


class ApiTestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api_tests'
    verbose_name = '接口测试'
