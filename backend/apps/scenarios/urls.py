from django.urls import path
from . import views

urlpatterns = [
    path('', views.ScenarioListCreateView.as_view(), name='scenario-list'),
    path('<uuid:pk>/', views.ScenarioDetailView.as_view(), name='scenario-detail'),
    path('<uuid:pk>/copy/', views.ScenarioCopyView.as_view(), name='scenario-copy'),
    path('<uuid:pk>/stats/', views.scenario_stats, name='scenario-stats'),
    path('import-har/', views.import_har, name='import-har'),
]
