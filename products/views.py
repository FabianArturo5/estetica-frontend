import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)


def products_catalog(request):
    """Vista para el catálogo de productos"""
    return render(request, 'products/catalog.html')


@require_http_methods(["GET"])
def get_products_api(request):
    """API proxy para obtener productos desde FastAPI"""
    try:
        skip = request.GET.get('skip', 0)
        limit = request.GET.get('limit', 100)
        search = request.GET.get('search', '')
        available_only = request.GET.get('available_only', 'false')
        
        fastapi_url = getattr(settings, 'FASTAPI_BASE_URL', 'http://fastapi:8000')
        url = f"{fastapi_url}/api/products/"
        
        params = {
            'skip': skip,
            'limit': limit,
            'available_only': available_only.lower() == 'true'
        }
        
        if search:
            params['search'] = search
        
        response = requests.get(url, params=params, timeout=10)
        return JsonResponse(response.json(), status=response.status_code, safe=False)
        
    except Exception as e:
        logger.error(f"Error en get_products_api: {e}")
        return JsonResponse({'detail': str(e)}, status=500)


@require_http_methods(["GET"])
def get_product_detail_api(request, product_id):
    """API proxy para obtener detalle de un producto"""
    try:
        fastapi_url = getattr(settings, 'FASTAPI_BASE_URL', 'http://fastapi:8000')
        url = f"{fastapi_url}/api/products/{product_id}"
        response = requests.get(url, timeout=10)
        return JsonResponse(response.json(), status=response.status_code)
        
    except Exception as e:
        logger.error(f"Error en get_product_detail_api: {e}")
        return JsonResponse({'detail': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_product_api(request):
    """API proxy para crear un producto (solo admin)"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'detail': 'No autenticado'}, status=401)
        
        data = json.loads(request.body)
        
        fastapi_url = getattr(settings, 'FASTAPI_BASE_URL', 'http://fastapi:8000')
        url = f"{fastapi_url}/api/products/"
        
        response = requests.post(
            url,
            json=data,
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Error en create_product_api: {e}")
        return JsonResponse({'detail': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def update_product_api(request, product_id):
    """API proxy para actualizar un producto (solo admin)"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'detail': 'No autenticado'}, status=401)
        
        data = json.loads(request.body)
        
        fastapi_url = getattr(settings, 'FASTAPI_BASE_URL', 'http://fastapi:8000')
        url = f"{fastapi_url}/api/products/{product_id}"
        
        response = requests.put(
            url,
            json=data,
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Error en update_product_api: {e}")
        return JsonResponse({'detail': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_product_api(request, product_id):
    """API proxy para eliminar un producto (solo admin)"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'detail': 'No autenticado'}, status=401)
        
        fastapi_url = getattr(settings, 'FASTAPI_BASE_URL', 'http://fastapi:8000')
        url = f"{fastapi_url}/api/products/{product_id}"
        
        response = requests.delete(
            url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        if response.status_code == 204:
            return JsonResponse({'message': 'Producto eliminado exitosamente'})
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except Exception as e:
        logger.error(f"Error en delete_product_api: {e}")
        return JsonResponse({'detail': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def upload_product_images_api(request, product_id):
    """API proxy para subir múltiples imágenes (solo admin)"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'detail': 'No autenticado'}, status=401)
        
        # Los archivos vienen en request.FILES
        files = request.FILES.getlist('images')
        
        if not files:
            return JsonResponse({'detail': 'No se enviaron imágenes'}, status=400)
        
        fastapi_url = getattr(settings, 'FASTAPI_BASE_URL', 'http://fastapi:8000')
        url = f"{fastapi_url}/api/products/{product_id}/upload-images"
        
        # Preparar archivos para enviar a FastAPI
        files_data = []
        for file in files:
            files_data.append(
                ('files', (file.name, file.read(), file.content_type))
            )
        
        response = requests.post(
            url,
            files=files_data,
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except Exception as e:
        logger.error(f"Error en upload_product_images_api: {e}")
        return JsonResponse({'detail': str(e)}, status=500)