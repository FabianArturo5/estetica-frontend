from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import requests
import json

# ==================== HELPER FUNCTION ====================

def get_fastapi_url(endpoint):
    """Helper para construir URLs correctas de FastAPI
    
    Args:
        endpoint: Ruta del endpoint (ej: '/trabajos/', '/auth/me', '/trabajos/123')
    
    Returns:
        URL completa del endpoint
    """
    base_url = getattr(settings, 'FASTAPI_BASE_URL', 'http://fastapi:8000')
    
    # Asegurarse que base_url no termine con /
    base_url = base_url.rstrip('/')
    
    # Asegurarse que endpoint empiece con /
    if not endpoint.startswith('/'):
        endpoint = f'/{endpoint}'
    
    # Si FASTAPI_BASE_URL ya incluye /api, no lo agregues de nuevo
    if base_url.endswith('/api'):
        return f"{base_url}{endpoint}"
    else:
        return f"{base_url}/api{endpoint}"

# ==================== VISTAS PÚBLICAS ====================

def galeria_trabajos(request):
    """Vista pública de galería de trabajos con filtros"""
    try:
        categoria = request.GET.get('categoria', '')
        search = request.GET.get('search', '')
        tag = request.GET.get('tag', '')
        destacados = request.GET.get('destacados', '')
        page = int(request.GET.get('page', 1))
        limit = 12
        skip = (page - 1) * limit
        
        params = {'skip': skip, 'limit': limit}
        if categoria:
            params['categoria'] = categoria
        if search:
            params['search'] = search
        if tag:
            params['tag'] = tag
        if destacados:
            params['destacados_only'] = 'true'
        
        response = requests.get(get_fastapi_url('/trabajos/'), params=params)
        trabajos = response.json() if response.status_code == 200 else []
        
        cat_response = requests.get(get_fastapi_url('/trabajos/categorias'))
        categorias = cat_response.json() if cat_response.status_code == 200 else []
        
        tags_response = requests.get(get_fastapi_url('/trabajos/tags/populares'), params={'limit': 15})
        tags_populares = tags_response.json() if tags_response.status_code == 200 else []
        
        context = {
            'trabajos': trabajos,
            'categorias': categorias,
            'tags_populares': tags_populares,
            'categoria_actual': categoria,
            'search_query': search,
            'tag_actual': tag,
            'page': page,
            'has_next': len(trabajos) == limit,
            'has_prev': page > 1,
        }
        
        return render(request, 'jobs/galeria.html', context)
    
    except Exception as e:
        messages.error(request, f'Error al cargar la galería: {str(e)}')
        return render(request, 'jobs/galeria.html', {'trabajos': [], 'categorias': []})

def detalle_trabajo(request, trabajo_id):
    """Vista de detalle de un trabajo específico"""
    try:
        response = requests.get(get_fastapi_url(f'/trabajos/{trabajo_id}'))
        
        if response.status_code == 404:
            messages.error(request, 'Trabajo no encontrado')
            return redirect('jobs:galeria')
        
        trabajo = response.json() if response.status_code == 200 else None
        
        relacionados = []
        if trabajo:
            rel_response = requests.get(
                get_fastapi_url('/trabajos/'),
                params={'categoria': trabajo['categoria'], 'limit': 4}
            )
            if rel_response.status_code == 200:
                relacionados = [t for t in rel_response.json() if t['id'] != trabajo_id][:3]
        
        context = {
            'trabajo': trabajo,
            'trabajos_relacionados': relacionados,
        }
        
        return render(request, 'jobs/detalle.html', context)
    
    except Exception as e:
        messages.error(request, f'Error al cargar el trabajo: {str(e)}')
        return redirect('jobs:galeria')

def trabajos_categoria(request, categoria):
    """Vista de trabajos filtrados por categoría"""
    return galeria_trabajos(request)

# ==================== VISTAS DE ADMINISTRACIÓN ====================

def admin_trabajos(request):
    """Panel de administración de trabajos - SIN @login_required"""
    print(f"🔍 DEBUG admin_trabajos - Path: {request.path}")
    print(f"🔍 DEBUG admin_trabajos - Method: {request.method}")
    
    try:
        # Verificar token en sesión
        token = request.session.get('access_token')
        print(f"🔍 DEBUG - Token presente: {bool(token)}")
        
        if not token:
            print("❌ No hay token, redirigiendo a login")
            messages.error(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('authentication:login_page')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Verificar si el usuario es admin usando FastAPI
        auth_url = get_fastapi_url('/auth/me')
        print(f"🔍 DEBUG - Verificando auth en: {auth_url}")
        
        auth_response = requests.get(auth_url, headers=headers, timeout=5)
        print(f"🔍 DEBUG - Auth response status: {auth_response.status_code}")
        
        if auth_response.status_code != 200:
            print(f"❌ Error de autenticación: {auth_response.status_code}")
            messages.error(request, 'Error de autenticación')
            return redirect('authentication:login_page')
        
        user_data = auth_response.json()
        print(f"🔍 DEBUG - User data: {user_data}")
        print(f"🔍 DEBUG - Is admin: {user_data.get('is_admin')}")
        
        if not user_data.get('is_admin'):
            print("❌ Usuario no es admin")
            messages.error(request, 'No tienes permisos de administrador')
            return redirect('jobs:galeria')
        
        print("✅ Usuario es admin, cargando trabajos...")
        
        # Obtener todos los trabajos
        page = int(request.GET.get('page', 1))
        limit = 20
        skip = (page - 1) * limit
        
        trabajos_url = get_fastapi_url('/trabajos/')
        print(f"🔍 DEBUG - Obteniendo trabajos de: {trabajos_url}")
        
        response = requests.get(
            trabajos_url,
            params={'skip': skip, 'limit': limit},
            headers=headers,
            timeout=5
        )
        
        print(f"🔍 DEBUG - Trabajos response status: {response.status_code}")
        
        if response.status_code == 401:
            messages.error(request, 'Sesión expirada')
            return redirect('authentication:login_page')
            
        trabajos = response.json() if response.status_code == 200 else []
        print(f"✅ Trabajos cargados: {len(trabajos)}")
        
        # Obtener estadísticas
        stats_response = requests.get(
            get_fastapi_url('/trabajos/estadisticas'), 
            headers=headers,
            timeout=5
        )
        estadisticas = stats_response.json() if stats_response.status_code == 200 else {}
        
        context = {
            'trabajos': trabajos,
            'estadisticas': estadisticas,
            'page': page,
            'has_next': len(trabajos) == limit,
            'has_prev': page > 1,
        }
        
        print("✅ Renderizando template admin/lista.html")
        return render(request, 'jobs/admin/lista.html', context)
    
    except requests.exceptions.Timeout:
        print("❌ Timeout conectando con FastAPI")
        messages.error(request, 'Timeout conectando con el servidor')
        return render(request, 'jobs/admin/lista.html', {'trabajos': []})
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Error de conexión: {str(e)}")
        messages.error(request, f'Error de conexión con el servidor: {str(e)}')
        return render(request, 'jobs/admin/lista.html', {'trabajos': []})
    except Exception as e:
        print(f"❌ ERROR en admin_trabajos: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error al cargar trabajos: {str(e)}')
        return render(request, 'jobs/admin/lista.html', {'trabajos': []})

def admin_crear_trabajo(request):
    """Crear nuevo trabajo - SIN @login_required"""
    print("=" * 80)
    print("🚀 INICIO admin_crear_trabajo")
    print(f"Method: {request.method}")
    print("=" * 80)
    
    try:
        token = request.session.get('access_token')
        if not token:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('authentication:login_page')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        auth_response = requests.get(get_fastapi_url('/auth/me'), headers=headers)
        if auth_response.status_code != 200:
            messages.error(request, 'Error de autenticación')
            return redirect('authentication:login_page')
        
        user_data = auth_response.json()
        if not user_data.get('is_admin'):
            messages.error(request, 'No tienes permisos de administrador')
            return redirect('jobs:galeria')
    
    except Exception as e:
        messages.error(request, f'Error de verificación: {str(e)}')
        return redirect('jobs:admin_trabajos')
    
    if request.method == 'GET':
        print("📄 Mostrando formulario (GET)")
        cat_response = requests.get(get_fastapi_url('/trabajos/categorias'))
        categorias = cat_response.json() if cat_response.status_code == 200 else []
        
        return render(request, 'jobs/admin/crear_editar.html', {
            'categorias': categorias,
            'trabajo': None
        })
    
    elif request.method == 'POST':
        print("📮 Procesando formulario (POST)")
        print(f"POST data: {dict(request.POST)}")
        print(f"FILES: {list(request.FILES.keys())}")
        
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Procesar tags
            tags_str = request.POST.get('tags', '').strip()
            print(f"🏷️  Tags string: '{tags_str}'")
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []
            print(f"🏷️  Tags procesados: {tags}")
            
            # Construir data
            titulo = request.POST.get('titulo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            categoria = request.POST.get('categoria', '').strip()
            destacado = request.POST.get('destacado') == 'on'
            
            print(f"📝 Título: '{titulo}'")
            print(f"📝 Descripción: '{descripcion[:50]}...' si descripcion else ''")
            print(f"📝 Categoría: '{categoria}'")
            print(f"⭐ Destacado: {destacado}")
            
            # Validar campos requeridos
            if not titulo:
                print("❌ ERROR: Título vacío")
                messages.error(request, 'El título es obligatorio')
                raise ValueError('Título vacío')
            
            if len(titulo) < 3:
                print("❌ ERROR: Título muy corto")
                messages.error(request, 'El título debe tener al menos 3 caracteres')
                raise ValueError('Título muy corto')
            
            if not categoria:
                print("❌ ERROR: Categoría vacía")
                messages.error(request, 'La categoría es obligatoria')
                raise ValueError('Categoría vacía')
            
            data = {
                'titulo': titulo,
                'descripcion': descripcion,
                'categoria': categoria,
                'destacado': destacado,
                'tags': tags,
            }
            
            # Procesar fecha
            fecha_realizacion = request.POST.get('fecha_realizacion', '').strip()
            print(f"📅 Fecha recibida: '{fecha_realizacion}'")
            
            if fecha_realizacion:
                from datetime import datetime
                try:
                    fecha_obj = datetime.strptime(fecha_realizacion, '%Y-%m-%d')
                    data['fecha_realizacion'] = fecha_obj.isoformat()
                    print(f"📅 Fecha procesada: '{data['fecha_realizacion']}'")
                except ValueError as ve:
                    print(f"⚠️  Error al parsear fecha: {ve}")
                    data['fecha_realizacion'] = fecha_realizacion
            
            print("\n" + "=" * 80)
            print("📤 DATOS A ENVIAR AL BACKEND:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=" * 80 + "\n")
            
            # Hacer request
            url = get_fastapi_url('/trabajos/')
            print(f"🌐 URL: {url}")
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"\n📡 RESPONSE STATUS: {response.status_code}")
            print(f"📡 RESPONSE BODY: {response.text}")
            print()
            
            if response.status_code == 201:
                trabajo = response.json()
                print(f"✅ Trabajo creado con ID: {trabajo.get('id')}")
                
                # Subir imágenes
                files = request.FILES.getlist('imagenes')
                if files:
                    print(f"📸 Subiendo {len(files)} imágenes...")
                    files_data = [('files', (f.name, f, f.content_type)) for f in files]
                    try:
                        img_response = requests.post(
                            get_fastapi_url(f'/trabajos/{trabajo["id"]}/upload-images'),
                            headers={'Authorization': f'Bearer {token}'},
                            files=files_data,
                            timeout=30
                        )
                        print(f"📸 Response status imágenes: {img_response.status_code}")
                        if img_response.status_code == 200:
                            print("✅ Imágenes subidas correctamente")
                        else:
                            print(f"⚠️  Error al subir imágenes: {img_response.text}")
                            messages.warning(request, 'Trabajo creado pero hubo un error al subir las imágenes')
                    except Exception as img_error:
                        print(f"❌ Error al subir imágenes: {str(img_error)}")
                        import traceback
                        traceback.print_exc()
                        messages.warning(request, 'Trabajo creado pero las imágenes no se pudieron subir')
                else:
                    print("ℹ️  No hay imágenes para subir")
                
                messages.success(request, '✅ Trabajo creado exitosamente')
                return redirect('jobs:admin_trabajos')
                
            elif response.status_code == 422:
                print("❌ ERROR 422: Validation Error")
                try:
                    error_detail = response.json()
                    print(f"Error detail: {json.dumps(error_detail, indent=2)}")
                    
                    if 'detail' in error_detail:
                        if isinstance(error_detail['detail'], list):
                            errores = []
                            for err in error_detail['detail']:
                                loc = err.get('loc', [])
                                campo = loc[-1] if loc else 'campo'
                                msg = err.get('msg', 'error')
                                
                                # Traducir nombres de campos
                                campo_es = {
                                    'titulo': 'Título',
                                    'descripcion': 'Descripción',
                                    'categoria': 'Categoría',
                                    'tags': 'Etiquetas'
                                }.get(campo, campo)
                                
                                # Traducir mensajes comunes
                                if 'at least' in msg and 'characters' in msg:
                                    import re
                                    match = re.search(r'at least (\d+)', msg)
                                    if match:
                                        min_chars = match.group(1)
                                        msg_es = f"debe tener al menos {min_chars} caracteres"
                                    else:
                                        msg_es = msg
                                else:
                                    msg_es = msg
                                
                                errores.append(f"{campo_es} {msg_es}")
                                print(f"  - {campo}: {msg}")
                            
                            messages.error(request, f'❌ {", ".join(errores)}')
                        else:
                            messages.error(request, f'Error de validación: {error_detail["detail"]}')
                    else:
                        messages.error(request, 'Error de validación en los datos enviados')
                except Exception as parse_error:
                    print(f"Error al parsear respuesta 422: {parse_error}")
                    messages.error(request, f'Error de validación (no se pudo parsear la respuesta)')
            else:
                print(f"❌ ERROR {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'Error desconocido')
                except:
                    error_detail = response.text or 'Sin respuesta del servidor'
                messages.error(request, f'Error al crear trabajo: {error_detail}')
        
        except ValueError as ve:
            print(f"❌ ValueError: {ve}")
            # Ya se mostró el mensaje
            pass
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT")
            messages.error(request, 'Timeout: El servidor tardó demasiado en responder')
        except requests.exceptions.ConnectionError as ce:
            print(f"❌ CONNECTION ERROR: {ce}")
            messages.error(request, f'Error de conexión: {str(ce)}')
        except Exception as e:
            print(f"❌ ERROR INESPERADO: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error inesperado: {str(e)}')
        
        # Recargar formulario con error
        print("🔄 Recargando formulario después de error")
        cat_response = requests.get(get_fastapi_url('/trabajos/categorias'))
        categorias = cat_response.json() if cat_response.status_code == 200 else []
        
        return render(request, 'jobs/admin/crear_editar.html', {
            'categorias': categorias,
            'trabajo': None
        })

def admin_editar_trabajo(request, trabajo_id):
    """Editar trabajo existente - SIN @login_required"""
    try:
        token = request.session.get('access_token')
        if not token:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('authentication:login_page')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        auth_response = requests.get(get_fastapi_url('/auth/me'), headers=headers)
        if auth_response.status_code != 200:
            messages.error(request, 'Error de autenticación')
            return redirect('authentication:login_page')
        
        user_data = auth_response.json()
        if not user_data.get('is_admin'):
            messages.error(request, 'No tienes permisos de administrador')
            return redirect('jobs:galeria')
    
    except Exception as e:
        messages.error(request, f'Error de verificación: {str(e)}')
        return redirect('jobs:admin_trabajos')
    
    if request.method == 'GET':
        try:
            response = requests.get(get_fastapi_url(f'/trabajos/{trabajo_id}'))
            trabajo = response.json() if response.status_code == 200 else None
            
            cat_response = requests.get(get_fastapi_url('/trabajos/categorias'))
            categorias = cat_response.json() if cat_response.status_code == 200 else []
            
            if not trabajo:
                messages.error(request, 'Trabajo no encontrado')
                return redirect('jobs:admin_trabajos')
            
            trabajo['tags_str'] = ', '.join(trabajo.get('tags', []))
            
            context = {
                'trabajo': trabajo,
                'categorias': categorias,
            }
            
            return render(request, 'jobs/admin/crear_editar.html', context)
        
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('jobs:admin_trabajos')
    
    elif request.method == 'POST':
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            tags_str = request.POST.get('tags', '')
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            
            data = {
                'titulo': request.POST.get('titulo'),
                'descripcion': request.POST.get('descripcion', ''),
                'categoria': request.POST.get('categoria'),
                'destacado': request.POST.get('destacado') == 'on',
                'tags': tags,
            }
            
            fecha_realizacion = request.POST.get('fecha_realizacion')
            if fecha_realizacion:
                data['fecha_realizacion'] = f'{fecha_realizacion}T00:00:00'
            
            response = requests.put(
                get_fastapi_url(f'/trabajos/{trabajo_id}'),
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                files = request.FILES.getlist('imagenes')
                if files:
                    files_data = [('files', (f.name, f, f.content_type)) for f in files]
                    img_response = requests.post(
                        get_fastapi_url(f'/trabajos/{trabajo_id}/upload-images'),
                        headers={'Authorization': f'Bearer {token}'},
                        files=files_data
                    )
                
                messages.success(request, 'Trabajo actualizado exitosamente')
                return redirect('jobs:admin_trabajos')
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                messages.error(request, f'Error al actualizar: {error_detail}')
        
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        cat_response = requests.get(get_fastapi_url('/trabajos/categorias'))
        categorias = cat_response.json() if cat_response.status_code == 200 else []
        
        response = requests.get(get_fastapi_url(f'/trabajos/{trabajo_id}'))
        trabajo = response.json() if response.status_code == 200 else None
        
        if trabajo:
            trabajo['tags_str'] = ', '.join(trabajo.get('tags', []))
        
        return render(request, 'jobs/admin/crear_editar.html', {
            'trabajo': trabajo,
            'categorias': categorias
        })

def admin_eliminar_trabajo(request, trabajo_id):
    """Eliminar trabajo - SIN @login_required"""
    try:
        token = request.session.get('access_token')
        if not token:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('authentication:login_page')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        auth_response = requests.get(get_fastapi_url('/auth/me'), headers=headers)
        if auth_response.status_code != 200:
            messages.error(request, 'Error de autenticación')
            return redirect('authentication:login_page')
        
        user_data = auth_response.json()
        if not user_data.get('is_admin'):
            messages.error(request, 'No tienes permisos de administrador')
            return redirect('jobs:galeria')
    
    except Exception as e:
        messages.error(request, f'Error de verificación: {str(e)}')
        return redirect('jobs:admin_trabajos')
    
    if request.method == 'POST':
        try:
            response = requests.delete(
                get_fastapi_url(f'/trabajos/{trabajo_id}'),
                headers=headers
            )
            
            if response.status_code == 204:
                messages.success(request, 'Trabajo eliminado exitosamente')
            else:
                messages.error(request, 'Error al eliminar trabajo')
        
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('jobs:admin_trabajos')

@require_http_methods(["POST"])
def admin_eliminar_imagen(request, trabajo_id, imagen_index):
    """Eliminar una imagen específica de un trabajo"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'error': 'No autorizado'}, status=401)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        auth_response = requests.get(get_fastapi_url('/auth/me'), headers=headers)
        if auth_response.status_code != 200:
            return JsonResponse({'error': 'Error de autenticación'}, status=401)
        
        user_data = auth_response.json()
        if not user_data.get('is_admin'):
            return JsonResponse({'error': 'No tienes permisos de administrador'}, status=403)
        
        response = requests.delete(
            get_fastapi_url(f'/trabajos/{trabajo_id}/images/{imagen_index}'),
            headers=headers
        )
        
        if response.status_code == 200:
            return JsonResponse({'success': True, 'message': 'Imagen eliminada'})
        else:
            return JsonResponse({'error': 'Error al eliminar imagen'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def admin_toggle_destacado(request, trabajo_id):
    """Marcar/desmarcar trabajo como destacado"""
    try:
        token = request.session.get('access_token')
        if not token:
            return JsonResponse({'error': 'No autorizado'}, status=401)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        auth_response = requests.get(get_fastapi_url('/auth/me'), headers=headers)
        if auth_response.status_code != 200:
            return JsonResponse({'error': 'Error de autenticación'}, status=401)
        
        user_data = auth_response.json()
        if not user_data.get('is_admin'):
            return JsonResponse({'error': 'No tienes permisos de administrador'}, status=403)
        
        data = json.loads(request.body)
        destacar = data.get('destacar', False)
        
        response = requests.patch(
            get_fastapi_url(f'/trabajos/{trabajo_id}/destacar'),
            headers=headers,
            json={'destacar': destacar}
        )
        
        if response.status_code == 200:
            return JsonResponse({'success': True, 'destacado': destacar})
        else:
            return JsonResponse({'error': 'Error al actualizar'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)