"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/scenarios/', include('apps.scenarios.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/environments/', include('apps.environments.urls')),
    path('api/v1/datasources/', include('apps.datasources.urls')),
    path('api/v1/api-tests/', include('apps.api_tests.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
