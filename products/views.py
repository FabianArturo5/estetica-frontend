import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods


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
        
        # Construir URL de FastAPI
        url = f"{settings.FASTAPI_BASE_URL}/api/products/"
        params = {
            'skip': skip,
            'limit': limit,
            'available_only': available_only.lower() == 'true'
        }
        
        if search:
            params['search'] = search
        
        response = requests.get(url, params=params, timeout=10)
        return JsonResponse(response.json(), status=response.status_code, safe=False)
        
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )


@require_http_methods(["GET"])
def get_product_detail_api(request, product_id):
    """API proxy para obtener detalle de un producto"""
    try:
        url = f"{settings.FASTAPI_BASE_URL}/api/products/{product_id}"
        response = requests.get(url, timeout=10)
        return JsonResponse(response.json(), status=response.status_code)
        
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'detail': f'Error conectando con el backend: {str(e)}'}, 
            status=503
        )