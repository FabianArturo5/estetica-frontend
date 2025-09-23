import requests
import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages

logger = logging.getLogger(__name__)

def get_fastapi_url(endpoint):
    """Helper para construir URLs correctas"""
    return f"{settings.FASTAPI_BASE_URL}/api/auth{endpoint}"

def is_authenticated(request):
    """Verificar si el usuario está autenticado"""
    return request.session.get('access_token') is not None

# Vistas para páginas HTML
def login_page(request):
    """Página de login"""
    if is_authenticated(request):
        return redirect('authentication:dashboard')
    return render(request, 'auth/login.html')

def register_page(request):
    """Página de registro"""
    if is_authenticated(request):
        return redirect('authentication:dashboard')
    return render(request, 'auth/register.html')

def forgot_password_page(request):
    """Página de recuperación de contraseña"""
    if is_authenticated(request):
        return redirect('authentication:dashboard')
    return render(request, 'auth/forgot_password.html')

def change_password_page(request):
    """Página para cambiar contraseña (requiere autenticación)"""
    if not is_authenticated(request):
        return redirect('authentication:login_page')
    return render(request, 'auth/change_password.html')

def dashboard_page(request):
    """Página principal del dashboard (requiere autenticación)"""
    if not is_authenticated(request):
        return redirect('authentication:login_page')
    return render(request, 'auth/dashboard.html')

# Vistas para API (con URLs corregidas)
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """Registrar nuevo usuario"""
    try:
        data = json.loads(request.body)
        
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {'detail': f'Campo requerido faltante: {field}'}, 
                    status=400
                )
        
        # URL CORREGIDA
        response = requests.post(
            get_fastapi_url('/register'),  # /api/auth/register
            json=data, 
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """Iniciar sesión y obtener token"""
    try:
        data = json.loads(request.body)
        
        if 'email' not in data or 'password' not in data:
            return JsonResponse(
                {'detail': 'Email y contraseña son requeridos'}, 
                status=400
            )
        
        # URL CORREGIDA
        response = requests.post(
            get_fastapi_url('/login'),  # /api/auth/login
            json=data, 
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            request.session['access_token'] = token_data.get('access_token')
            request.session['token_type'] = token_data.get('token_type')
            request.session['user_email'] = data.get('email')
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """Cerrar sesión"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'detail': 'No autenticado'}, status=401)
        
        # URL CORREGIDA
        response = requests.post(
            get_fastapi_url('/logout'),  # /api/auth/logout
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        request.session.flush()
        return JsonResponse({'message': 'Sesión cerrada exitosamente'})
        
    except Exception as e:
        # Siempre limpiar la sesión, incluso si hay error
        request.session.flush()
        return JsonResponse({'message': 'Sesión cerrada'})

def logout_page(request):
    """Cerrar sesión y redirigir"""
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('authentication:login_page')

@require_http_methods(["GET"])
def get_current_user(request):
    """Obtener información del usuario actual"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'detail': 'No autenticado'}, status=401)
        
        # URL CORREGIDA
        response = requests.get(
            get_fastapi_url('/me'),  # /api/auth/me
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )

@csrf_exempt
@require_http_methods(["PUT"])
def change_password(request):
    """Cambiar contraseña del usuario autenticado"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'detail': 'No autenticado'}, status=401)
        
        data = json.loads(request.body)
        
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {'detail': f'Campo requerido faltante: {field}'}, 
                    status=400
                )
        
        # URL CORREGIDA
        response = requests.put(
            get_fastapi_url('/change-password'),  # /api/auth/change-password
            json=data,
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )

@csrf_exempt
@require_http_methods(["POST"])
def forgot_password(request):
    """Solicitar código de recuperación de contraseña"""
    try:
        data = json.loads(request.body)
        
        if 'email' not in data:
            return JsonResponse({'detail': 'Email es requerido'}, status=400)
        
        # URL CORREGIDA
        response = requests.post(
            get_fastapi_url('/forgot-password'),  # /api/auth/forgot-password
            json=data,
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )

@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    """Restablecer contraseña usando código de recuperación"""
    try:
        data = json.loads(request.body)
        
        required_fields = ['email', 'reset_code', 'new_password', 'confirm_password']
        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {'detail': f'Campo requerido faltante: {field}'}, 
                    status=400
                )
        
        # URL CORREGIDA
        response = requests.post(
            get_fastapi_url('/reset-password'),  # /api/auth/reset-password
            json=data,
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )

@csrf_exempt
@require_http_methods(["POST"])
def verify_reset_code(request):
    """Verificar si un código de recuperación es válido"""
    try:
        data = json.loads(request.body)
        
        if 'email' not in data or 'reset_code' not in data:
            return JsonResponse(
                {'detail': 'Email y reset_code son requeridos'}, 
                status=400
            )
        
        # URL CORREGIDA
        response = requests.post(
            get_fastapi_url('/verify-reset-code'),  # /api/auth/verify-reset-code
            json=data,
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )