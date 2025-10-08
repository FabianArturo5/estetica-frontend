from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # URLs públicas
    path('', views.galeria_trabajos, name='galeria'),
    path('trabajo/<str:trabajo_id>/', views.detalle_trabajo, name='detalle'),
    path('categoria/<str:categoria>/', views.trabajos_categoria, name='categoria'),
    
    # URLs de administración
    path('admin/', views.admin_trabajos, name='admin_trabajos'),  # ← ESTA ES LA IMPORTANTE
    path('admin/crear/', views.admin_crear_trabajo, name='admin_crear_trabajo'),
    path('admin/editar/<str:trabajo_id>/', views.admin_editar_trabajo, name='admin_editar_trabajo'),
    path('admin/eliminar/<str:trabajo_id>/', views.admin_eliminar_trabajo, name='admin_eliminar_trabajo'),
    
    # APIs para AJAX
    path('admin/trabajo/<str:trabajo_id>/imagen/<int:imagen_index>/eliminar/', 
         views.admin_eliminar_imagen, name='admin_eliminar_imagen'),
    path('admin/trabajo/<str:trabajo_id>/toggle-destacado/', 
         views.admin_toggle_destacado, name='admin_toggle_destacado'),
]