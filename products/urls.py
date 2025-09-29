from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Vista del catálogo (HTML)
    path('', views.products_catalog, name='catalog'),
    
    # API endpoints - IMPORTANTE: sin 'api/' al inicio
    path('api/', views.get_products_api, name='api_list'),
    path('api/<str:product_id>/', views.get_product_detail_api, name='api_detail'),
]