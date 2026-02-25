from django.urls import path
from . import views

urlpatterns = [
    path('', views.EnvironmentListCreateView.as_view(), name='environment-list'),
    path('<uuid:pk>/', views.EnvironmentDetailView.as_view(), name='environment-detail'),
    path('<uuid:pk>/set-default/', views.set_default_environment, name='environment-set-default'),
    path('<uuid:pk>/preview/', views.preview_variables, name='environment-preview'),
    path('<uuid:pk>/variables/', views.VariableListCreateView.as_view(), name='variable-list'),
    path('<uuid:pk>/variables/<uuid:variable_pk>/', views.VariableDetailView.as_view(), name='variable-detail'),
    path('default/', views.get_default_environment, name='environment-default'),
]
