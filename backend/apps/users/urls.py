from django.urls import path
from . import views
from . import views_extra

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard_stats, name='dashboard'),
    path('my-permissions/', views_extra.get_current_user_permissions, name='my-permissions'),
    path('', views_extra.UserListView.as_view(), name='users-list'),
    path('<str:pk>/', views_extra.UserDetailView.as_view(), name='user-detail'),
    path('<str:pk>/role/', views_extra.update_user_role, name='update-user-role'),
]
