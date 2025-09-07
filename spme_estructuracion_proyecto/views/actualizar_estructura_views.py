# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from spme_estructuracion_proyecto.models import (
    DiagramaEstructura, Proyecto, ObjetivoGeneralProyecto, ObjetivoEspecificoProyecto,
    ResultadoOG, ResultadoOE, Proceso, ProductoOE, ProductoResultadoOE
)
from ..serializers.actualizar_estructura_serializer import *
import logging

logger = logging.getLogger(__name__)

# views.py
@api_view(['PUT'])
@transaction.atomic
def actualizar_estructura_diagrama(request, diagrama_id):
    """
    Endpoint para actualizar la estructura completa y diagrama usando el ID del diagrama
    """
    try:
        print("=== INICIANDO ACTUALIZACIÓN ===")
        
        # Obtener el diagrama por ID
        diagrama = get_object_or_404(DiagramaEstructura, id=diagrama_id)
        proyecto = diagrama.proyecto
        print(f"Proyecto: {proyecto.codigo}")
        
        datos_diagrama = request.data
        
        # 1. Actualizar el diagrama de estructura
        diagrama.codigoProyecto = datos_diagrama.get('codigoProyecto', diagrama.codigoProyecto)
        diagrama.nodos = datos_diagrama.get('nodos', diagrama.nodos)
        diagrama.conexiones = datos_diagrama.get('conexiones', diagrama.conexiones)
        diagrama.sincronizado = True
        diagrama.save()
        print("Diagrama guardado")
        
        # 2. Actualizar los modelos asociados a cada nodo
        nodos = datos_diagrama.get('nodos', [])
        nodos_actualizados = 0
        errores = []
        
        for i, nodo in enumerate(nodos):
            tipo_nodo = nodo.get('type', '')
            datos_nodo = nodo.get('data', {})
            
            print(f"\n--- Procesando nodo {i} ---")
            print(f"Tipo: {tipo_nodo}")
            print(f"Keys en data: {list(datos_nodo.keys())}")
            
            # CORRECCIÓN: Diferente estructura para proyecto vs otros nodos
            if tipo_nodo == 'proyecto':
                # Para nodos proyecto: datos en 'datosNodo'
                nodo_proyecto_data = datos_nodo.get('datosNodo', {})
                print(f"Buscando en 'datosNodo': {list(nodo_proyecto_data.keys()) if nodo_proyecto_data else 'VACIO'}")
            else:
                # Para otros nodos: datos en 'nodoProyecto'
                nodo_proyecto_data = datos_nodo.get('nodoProyecto', {})
                print(f"Buscando en 'nodoProyecto': {list(nodo_proyecto_data.keys()) if nodo_proyecto_data else 'VACIO'}")
            
            if not nodo_proyecto_data:
                print(f"Nodo {i} sin datos, saltando")
                continue
            
            print(f"Datos a procesar: {list(nodo_proyecto_data.keys())}")
            
            try:
                # Preprocesar fechas
                processed_data = preprocesar_fechas(nodo_proyecto_data)
                
                if tipo_nodo == 'proyecto':
                    print("Actualizando PROYECTO...")
                    proyecto_serializer = ProyectoSerializer(proyecto, data=processed_data, partial=True)
                    if proyecto_serializer.is_valid():
                        proyecto_actualizado = proyecto_serializer.save()
                        nodos_actualizados += 1
                        print(f"✅ Proyecto actualizado: {proyecto_actualizado.codigo}")
                    else:
                        error_msg = f"Error validando proyecto: {proyecto_serializer.errors}"
                        print(f"❌ {error_msg}")
                        raise serializers.ValidationError(error_msg)
                
                elif tipo_nodo == 'objetivogeneral':
                    print("Actualizando OBJETIVO GENERAL...")
                    objetivo_id = processed_data.get('id')
                    if objetivo_id:
                        objetivo = ObjetivoGeneralProyecto.objects.get(id=objetivo_id, proyecto=proyecto)
                        objetivo_serializer = ObjetivoGeneralSerializer(objetivo, data=processed_data, partial=True)
                        if objetivo_serializer.is_valid():
                            objetivo_serializer.save()
                            nodos_actualizados += 1
                            print(f"✅ Objetivo general {objetivo_id} actualizado")
                        else:
                            error_msg = f"Error validando objetivo general: {objetivo_serializer.errors}"
                            raise serializers.ValidationError(error_msg)
                    else:
                        error_msg = "Objetivo general sin ID"
                        raise serializers.ValidationError(error_msg)
                
                elif tipo_nodo == 'objetivoespecificoog':
                    print("Actualizando OBJETIVO ESPECÍFICO OG...")
                    objetivo_id = processed_data.get('id')
                    print(objetivo_id)
                    if objetivo_id:
                        objetivo = ObjetivoEspecificoProyecto.objects.get(id=objetivo_id)
                        print(objetivo)
                        objetivo_serializer = ObjetivoEspecificoSerializer(objetivo, data=processed_data, partial=True)
                        if objetivo_serializer.is_valid():
                            objetivo_serializer.save()
                            nodos_actualizados += 1
                            print(f"✅ Objetivo específico {objetivo_id} actualizado")
                        else:
                            error_msg = f"Error validando objetivo específico: {objetivo_serializer.errors}"
                            raise serializers.ValidationError(error_msg)
                    else:
                        error_msg = "Objetivo específico sin ID"
                        raise serializers.ValidationError(error_msg)
                
                elif tipo_nodo == 'resultadoog':
                    print("Actualizando RESULTADO OG...")
                    resultado_id = processed_data.get('id')
                    if resultado_id:
                        resultado = ResultadoOG.objects.get(id=resultado_id)
                        resultado_serializer = ResultadoOGSerializer(resultado, data=processed_data, partial=True)
                        if resultado_serializer.is_valid():
                            resultado_serializer.save()
                            nodos_actualizados += 1
                            print(f"✅ Resultado OG {resultado_id} actualizado")
                        else:
                            error_msg = f"Error validando resultado OG: {resultado_serializer.errors}"
                            raise serializers.ValidationError(error_msg)
                    else:
                        error_msg = "Resultado OG sin ID"
                        raise serializers.ValidationError(error_msg)
                
                elif tipo_nodo == 'resultadooe':
                    print("Actualizando RESULTADO OE...")
                    resultado_id = processed_data.get('id')
                    if resultado_id:
                        resultado = ResultadoOE.objects.get(id=resultado_id)
                        resultado_serializer = ResultadoOESerializer(resultado, data=processed_data, partial=True)
                        if resultado_serializer.is_valid():
                            resultado_serializer.save()
                            nodos_actualizados += 1
                            print(f"✅ Resultado OE {resultado_id} actualizado")
                        else:
                            error_msg = f"Error validando resultado OE: {resultado_serializer.errors}"
                            raise serializers.ValidationError(error_msg)
                    else:
                        error_msg = "Resultado OE sin ID"
                        raise serializers.ValidationError(error_msg)
                
                elif tipo_nodo == 'procesorog':
                    print("Actualizando PROCESO...")
                    proceso_id = processed_data.get('id')
                    if proceso_id:
                        proceso = Proceso.objects.get(id=proceso_id)
                        proceso_serializer = ProcesoSerializer(proceso, data=processed_data, partial=True)
                        if proceso_serializer.is_valid():
                            proceso_serializer.save()
                            nodos_actualizados += 1
                            print(f"✅ Proceso {proceso_id} actualizado")
                        else:
                            error_msg = f"Error validando proceso: {proceso_serializer.errors}"
                            raise serializers.ValidationError(error_msg)
                    else:
                        error_msg = "Proceso sin ID"
                        raise serializers.ValidationError(error_msg)
                
                elif tipo_nodo == 'productooe':
                    print("Actualizando PRODUCTO OE...")
                    producto_id = processed_data.get('id')
                    if producto_id:
                        producto = ProductoOE.objects.get(id=producto_id)
                        producto_serializer = ProductoOESerializer(producto, data=processed_data, partial=True)
                        if producto_serializer.is_valid():
                            producto_serializer.save()
                            nodos_actualizados += 1
                            print(f"✅ Producto OE {producto_id} actualizado")
                        else:
                            error_msg = f"Error validando producto OE: {producto_serializer.errors}"
                            raise serializers.ValidationError(error_msg)
                    else:
                        error_msg = "Producto OE sin ID"
                        raise serializers.ValidationError(error_msg)
                
                elif tipo_nodo == 'productoresultadooe':
                    print("Actualizando PRODUCTO RESULTADO OE...")
                    producto_id = processed_data.get('id')
                    if producto_id:
                        producto = ProductoResultadoOE.objects.get(id=producto_id)
                        producto_serializer = ProductoResultadoOESerializer(producto, data=processed_data, partial=True)
                        if producto_serializer.is_valid():
                            producto_serializer.save()
                            nodos_actualizados += 1
                            print(f"✅ Producto resultado OE {producto_id} actualizado")
                        else:
                            error_msg = f"Error validando producto resultado OE: {producto_serializer.errors}"
                            raise serializers.ValidationError(error_msg)
                    else:
                        error_msg = "Producto resultado OE sin ID"
                        raise serializers.ValidationError(error_msg)
                
                else:
                    print(f"⚠️  Tipo de nodo no reconocido: {tipo_nodo}")
                        
            except serializers.ValidationError as ve:
                print(f"❌ Error de validación: {ve.detail}")
                raise ve
            except Exception as e:
                error_msg = f"Error procesando nodo {i}: {str(e)}"
                print(f"❌ {error_msg}")
                raise serializers.ValidationError(error_msg)
        
        response_data = {
            'message': 'Estructura y diagrama actualizados exitosamente',
            'diagrama_id': diagrama.id,
            'proyecto_id': proyecto.id,
            'proyecto_codigo': proyecto.codigo,
            'nodos_procesados': len(nodos),
            'nodos_actualizados': nodos_actualizados,
            'errores': errores,
            'sincronizado': True
        }
        
        print(f"✅ Operación completada: {nodos_actualizados} nodos actualizados")
        return Response(response_data, status=status.HTTP_200_OK)
    
    except serializers.ValidationError as ve:
        print(f"❌ Error de validación (ROLLBACK): {ve.detail}")
        return Response(
            {'error': 'Error de validación en los datos', 'detalles': ve.detail},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(f"❌ Error crítico (ROLLBACK): {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
def preprocesar_fechas(data):
    """
    Función para preprocesar y normalizar formatos de fecha
    """
    from django.utils.dateparse import parse_date
    from datetime import datetime
    import re
    
    processed = data.copy()
    
    # Mapeo de campos de fecha comunes
    date_fields = [
        'fecha_inicio', 'fecha_finalizacion', 'fecha_creacion',
        'fecha_programada', 'fecha_inicio', 'fecha_cierre',
        'fecha_baseline', 'fecha_target_q1', 'fecha_target_q2',
        'fecha_target_q3', 'fecha_target_q4', 'fecha_solicitud',
        'fecha_realizacion_actividad'
    ]
    
    for field in date_fields:
        if field in processed and processed[field]:
            try:
                value = processed[field]
                print(f"Procesando fecha {field}: {value} (tipo: {type(value)})")
                
                # Si ya es objeto date, no hacer nada
                if hasattr(value, 'strftime'):
                    continue
                    
                # Si es string, intentar parsear
                if isinstance(value, str):
                    # Intentar diferentes formatos
                    parsed_date = None
                    
                    # Formato ISO (YYYY-MM-DD)
                    if re.match(r'^\d{4}-\d{2}-\d{2}', value):
                        parsed_date = parse_date(value)
                    
                    # Formato DD/MM/YYYY
                    elif re.match(r'^\d{2}/\d{2}/\d{4}', value):
                        try:
                            parsed_date = datetime.strptime(value, '%d/%m/%Y').date()
                        except:
                            pass
                    
                    # Formato MM/DD/YYYY
                    elif re.match(r'^\d{2}/\d{2}/\d{4}', value):
                        try:
                            parsed_date = datetime.strptime(value, '%m/%d/%Y').date()
                        except:
                            pass
                    
                    if parsed_date:
                        processed[field] = parsed_date
                        print(f"✅ Fecha {field} convertida: {parsed_date}")
                    else:
                        print(f"⚠️  No se pudo convertir fecha {field}: {value}")
                        # Mantener el valor original pero como string
                        
            except Exception as e:
                print(f"❌ Error procesando fecha {field}: {e}")
                # En caso de error, mantener el valor original
    
    return processed    