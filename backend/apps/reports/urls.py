from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportListCreateView.as_view(), name='report-list'),
    path('<uuid:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('<uuid:pk>/run/', views.run_load_test, name='report-run'),
    # path('<uuid:pk>/stop/', views.stop_load_test, name='report-stop'),
    path('<uuid:pk>/stats/', views.get_load_test_stats, name='report-stats'),
    path('<uuid:pk>/export/pdf/', views.export_report_pdf, name='report-export-pdf'),
    path('<uuid:pk>/export/excel/', views.export_report_excel, name='report-export-excel'),
    path('compare/', views.compare_reports, name='report-compare'),
]
