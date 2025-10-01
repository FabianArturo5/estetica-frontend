from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Vista del catálogo (HTML)
    path('', views.products_catalog, name='catalog'),
    
    # API endpoints de administración (más específicos primero)
    path('api/create/', views.create_product_api, name='api_create'),
    path('api/<str:product_id>/update/', views.update_product_api, name='api_update'),
    path('api/<str:product_id>/delete/', views.delete_product_api, name='api_delete'),
    path('api/<str:product_id>/upload-images/', views.upload_product_images_api, name='api_upload_images'),  # NUEVO
    # API endpoints públicos
    path('api/', views.get_products_api, name='api_list'),
    path('api/<str:product_id>/', views.get_product_detail_api, name='api_detail'),
]