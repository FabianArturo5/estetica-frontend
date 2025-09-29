from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Vista del catálogo (HTML)
    path('', views.products_catalog, name='catalog'),
    
    # API endpoints de administración - DEBEN IR PRIMERO
    path('api/create/', views.create_product_api, name='api_create'),
    path('api/<str:product_id>/update/', views.update_product_api, name='api_update'),
    path('api/<str:product_id>/delete/', views.delete_product_api, name='api_delete'),
    
    # API endpoints públicos - DESPUÉS
    path('api/', views.get_products_api, name='api_list'),
    path('api/<str:product_id>/', views.get_product_detail_api, name='api_detail'),
]