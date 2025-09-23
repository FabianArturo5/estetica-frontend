import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    """Vista principal"""
    context = {
        'title': 'Estética Frontend',
        'fastapi_url': settings.FASTAPI_BASE_URL
    }
    return render(request, 'index.html', context)
