from django.urls import path
from . import views

urlpatterns = [
    # 测试套件
    path('suites/', views.TestSuiteListCreateView.as_view(), name='suite-list'),
    path('suites/<uuid:pk>/', views.TestSuiteDetailView.as_view(), name='suite-detail'),
    
    # 测试用例
    path('suites/<uuid:suite_id>/cases/', views.TestCaseListCreateView.as_view(), name='case-list'),
    path('cases/<uuid:pk>/', views.TestCaseDetailView.as_view(), name='case-detail'),
    
    # 断言
    path('cases/<uuid:test_case_id>/assertions/', views.AssertionListCreateView.as_view(), name='assertion-list'),
    path('assertions/<uuid:pk>/', views.AssertionDetailView.as_view(), name='assertion-detail'),
    
    # 测试结果
    path('results/', views.TestResultListView.as_view(), name='result-list'),
    
    # 执行测试
    path('execute/', views.execute_test, name='test-execute'),
    path('execute-request/', views.execute_single_request, name='test-execute-request'),
]
