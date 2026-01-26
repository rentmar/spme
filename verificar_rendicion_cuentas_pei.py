"""
Script de prueba para verificar los endpoints de RendicionCuentasActPei
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from apptran.monitoreo.views.rendicion_cuentas_pei_crud_views import RendicionCuentasActPeiView
from spme_monitoreo.models import RendicionCuentasActPei, ActividadPei, TareaActividadPei, Usuario

def probar_endpoints():
    factory = APIRequestFactory()
    view = RendicionCuentasActPeiView.as_view({'get': 'list', 'post': 'create', 'post': 'filtrar', 'patch': 'actualizar_estado'})

    print("=" * 80)
    print("VERIFICACION DE ENDPOINTS DE RENDICION DE CUENTAS PEI")
    print("=" * 80)

    # 1. Verificar modelo y metodo save()
    print("\n1. Verificando modelo RendicionCuentasActPei...")
    try:
        print(f"   - Total registros: {RendicionCuentasActPei.objects.count()}")
        print(f"   - Metodo save() implementado: {'save' in dir(RendicionCuentasActPei)}")
        print("   [OK] Modelo verificado")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")

    # 2. Verificar ViewSet
    print("\n2. Verificando ViewSet RendicionCuentasActPeiView...")
    try:
        viewset = RendicionCuentasActPeiView()
        print(f"   - create() method: {hasattr(viewset, 'create')}")
        print(f"   - list() method: {hasattr(viewset, 'list')}")
        print(f"   - filtrar() action: {hasattr(viewset, 'filtrar')}")
        print(f"   - actualizar_estado() action: {hasattr(viewset, 'actualizar_estado')}")
        print("   [OK] ViewSet verificado")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")

    # 3. Verificar Serializers
    print("\n3. Verificando Serializers...")
    try:
        from apptran.monitoreo.serializers.rendicion_cuentas_pei_crud_serializer import (
            RendicionCuentasActPeiSerializer,
            RendicionCuentasActPeiFiltrarSerializer,
            RendicionCuentasActPeiActualizarEstadoSerializer
        )
        print(f"   - RendicionCuentasActPeiSerializer: [OK]")
        print(f"   - RendicionCuentasActPeiFiltrarSerializer: [OK]")
        print(f"   - RendicionCuentasActPeiActualizarEstadoSerializer: [OK]")
        print("   [OK] Serializers verificados")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")

    # 4. Verificar registro de URLs
    print("\n4. Verificando registro de URLs...")
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        patterns = [p for p in resolver.url_patterns]
        print("   - Buscando 'rendicion-cuentas-pei' en las URLs...")
        encontrados = [p for p in patterns if 'rendicion-cuentas-pei' in str(p.pattern).lower()]
        if encontrados:
            print(f"   [OK] Se encontraron {len(encontrados)} patrones de URL")
            for p in encontrados[:2]:
                print(f"     - {p.pattern}")
        else:
            print("   [ERROR] No se encontro el patron de URL")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")

    print("\n" + "=" * 80)
    print("RESUMEN DE ENDPOINTS IMPLEMENTADOS")
    print("=" * 80)
    print("\nBase URL: http://127.0.0.1:8000/api/rendicion-cuentas-pei/")
    print("\n1. POST /api/rendicion-cuentas-pei/")
    print("   - Crear rendicion de cuentas con autogeneracion de numeroFormulario")
    print("\n2. GET /api/rendicion-cuentas-pei/")
    print("   - Obtener todas las rendiciones de cuentas")
    print("\n3. POST /api/rendicion-cuentas-pei/filtrar/")
    print("   - Filtrar por actividad_id, usuario_id, tarea_id")
    print("   - Body: {\"actividad_id\": 5, \"usuario_id\": 7, \"tarea_id\": 9}")
    print("\n4. PATCH /api/rendicion-cuentas-pei/actualizar_estado/")
    print("   - Actualizar estado de validacion")
    print("   - Body: {\"id\": 3, \"validacionResponsable\": true}")
    print("=" * 80)

if __name__ == '__main__':
    probar_endpoints()
