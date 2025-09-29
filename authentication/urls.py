from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Páginas HTML
    path('', views.dashboard_page, name='dashboard'),  # Página principal del dashboard
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('forgot_password/', views.forgot_password_page, name='forgot_password_page'),
    path('change-password/', views.change_password_page, name='change_password_page'),
    path('dashboard/', views.dashboard_page, name='dashboard_page'),
    path('logout/', views.logout_page, name='logout_page'),  # URL para cerrar sesión directamente
    
    # Endpoints API - IMPORTANTE: Las URLs de la API deben ir ANTES que las páginas HTML genéricas
    path('api/register/', views.register, name='register_api'),
    path('api/login/', views.login_view, name='login_api'),
    path('api/logout/', views.logout_view, name='logout_api'),
    path('api/me/', views.get_current_user, name='current_user_api'),
    path('api/change-password/', views.change_password, name='change_password_api'),
    path('api/forgot_password/', views.forgot_password, name='forgot_password_api'),
    path('api/reset-password/', views.reset_password, name='reset_password_api'),
    path('api/verify-reset-code/', views.verify_reset_code, name='verify_reset_code_api'),
]