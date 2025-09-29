import requests
from django.http import JsonResponse
from django.conf import settings


def check_admin_permission(request):
    """Helper para verificar permisos de administrador"""
    token = request.session.get('access_token')
    
    if not token:
        return False, JsonResponse({'detail': 'No autenticado'}, status=401)
    
    try:
        response = requests.get(
            f"{settings.FASTAPI_BASE_URL}/api/auth/me",
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            is_admin = user_data.get('is_admin', False) or user_data.get('role') == 'admin'
            
            if not is_admin:
                return False, JsonResponse(
                    {'detail': 'Permisos de administrador requeridos'}, 
                    status=403
                )
            
            return True, None
        else:
            return False, JsonResponse({'detail': 'Token inválido'}, status=401)
            
    except Exception as e:
        return False, JsonResponse(
            {'detail': 'Error al verificar permisos'}, 
            status=503
        )


def is_authenticated(request):
    """Helper para verificar autenticación básica"""
    return request.session.get('access_token') is not None