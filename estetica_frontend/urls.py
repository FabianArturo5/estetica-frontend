from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render

def home_view(request):
    """Vista de la página principal"""
    return render(request, 'index.html', {
        'title': 'Estética Lucy SYFAHG',
        'FASTAPI_BASE_URL': getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
    })

def health_check(request):
    """Health check simple"""
    return HttpResponse("OK - Django funcionando correctamente")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Página principal
    path('health/', health_check, name='health_check'),
    path('auth/', include('authentication.urls')),  # Incluir las URLs de autenticación
]