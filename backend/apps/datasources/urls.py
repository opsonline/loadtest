from django.urls import path
from . import views

urlpatterns = [
    path('', views.DataSourceListCreateView.as_view(), name='datasource-list'),
    path('<uuid:pk>/', views.DataSourceDetailView.as_view(), name='datasource-detail'),
    path('<uuid:pk>/test/', views.test_connection, name='datasource-test'),
    path('<uuid:pk>/preview/', views.preview_data, name='datasource-preview'),
    path('<uuid:pk>/data/', views.get_data_by_index, name='datasource-data'),
    path('upload/', views.upload_file, name='datasource-upload'),
    path('types/', views.list_source_types, name='datasource-types'),
]
