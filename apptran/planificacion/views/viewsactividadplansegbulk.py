# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from spme_actividades.models import Actividad
# from .serializeractividadbulk import ActividadBulkSerializer
from ..serializadores.serializadoractivadesplanificacionseguimientobulk import ActividadBulkSerializer
from spme_planificacion.models import PlanificacionProyecto, CambioPlanificacion 
import json
from datetime import datetime

@api_view(['POST'])
@transaction.atomic
def procesar_actividades_planificacion_bulk(request, idproyecto=None):
    """
    Procesa un array de actividades (crear o actualizar) y registra la planificación
    POST /actividades/procesar-bulk/<idproyecto>/
    """
    try:
        # Validar que se proporcione el ID del proyecto
        if not idproyecto:
            return Response(
                {'error': 'Se requiere el ID del proyecto en la URL'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener el proyecto
        from spme_estructuracion_proyecto.models import Proyecto
        proyecto = get_object_or_404(Proyecto, id=idproyecto)
        
        # Obtener datos de la solicitud
        request_data = request.data
        
        # Verificar si es un array simple o un objeto con metadata
        if isinstance(request_data, list):
            # Formato antiguo: solo array de actividades
            actividades_data = request_data
            table_config = None
            cambio_planificacion_data = None
            usuario_nick = None
        else:
            # Formato nuevo: objeto con metadata y actividades
            actividades_data = request_data.get('rows_data', [])
            table_config = request_data.get('table_config', None)
            cambio_planificacion_data = request_data.get('cambio_planificacion', None)
            usuario_nick = request_data.get('usuario', None)
        
        if not isinstance(actividades_data, list):
            return Response(
                {'error': 'Se esperaba un array de actividades'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultados = {
            'creadas': 0,
            'actualizadas': 0,
            'errores': [],
            'detalles': [],
            'planificacion_id': None,
            'version': None
        }
        
        # Obtener información del usuario (prioridad: metadata > usuario autenticado)
        usuario = usuario_nick
        if not usuario and hasattr(request, 'user') and request.user.is_authenticated:
            usuario = request.user.username
        
        # Procesar cada actividad
        for index, actividad_data in enumerate(actividades_data):
            try:
                # Asegurar que la actividad pertenece al proyecto correcto
                actividad_data['proyecto_id'] = idproyecto
                
                # Determinar si es creación o actualización
                actividad_id = actividad_data.get('id', 0)
                
                if actividad_id == 0:
                    # Crear nueva actividad
                    serializer = ActividadBulkSerializer(data=actividad_data)
                    if serializer.is_valid():
                        actividad = serializer.save()
                        resultados['creadas'] += 1
                        resultados['detalles'].append({
                            'index': index,
                            'id': actividad.id,
                            'accion': 'creada',
                            'estado': 'éxito'
                        })
                    else:
                        resultados['errores'].append({
                            'index': index,
                            'error': serializer.errors,
                            'accion': 'crear'
                        })
                
                else:
                    # Actualizar actividad existente
                    try:
                        actividad = Actividad.objects.get(id=actividad_id, proyecto=proyecto)
                        
                        # Guardar datos anteriores para el registro de cambios
                        datos_anteriores = {
                            'codigo': actividad.codigo,
                            'nombreCorto': actividad.nombreCorto,
                            'tipo': str(actividad.tipo),
                            'responsable': actividad.responsable.username if actividad.responsable else None,
                            'fecha_inicio': actividad.fecha_inicio,
                            'fecha_cierre': actividad.fecha_cierre,
                            'presupuesto': actividad.presupuesto,
                            'estado': actividad.estado
                        }
                        
                        serializer = ActividadBulkSerializer(actividad, data=actividad_data, partial=True)
                        if serializer.is_valid():
                            actividad_actualizada = serializer.save()
                            resultados['actualizadas'] += 1
                            resultados['detalles'].append({
                                'index': index,
                                'id': actividad_id,
                                'accion': 'actualizada',
                                'estado': 'éxito'
                            })
                            
                        else:
                            resultados['errores'].append({
                                'index': index,
                                'id': actividad_id,
                                'error': serializer.errors,
                                'accion': 'actualizar'
                            })
                    except Actividad.DoesNotExist:
                        resultados['errores'].append({
                            'index': index,
                            'id': actividad_id,
                            'error': 'Actividad no encontrada en este proyecto',
                            'accion': 'actualizar'
                        })
            
            except Exception as e:
                resultados['errores'].append({
                    'index': index,
                    'id': actividad_data.get('id', 'desconocido'),
                    'error': str(e),
                    'accion': 'procesar'
                })
        
        # Almacenar la planificación completa
        try:
            # Obtener la última versión
            ultima_version = PlanificacionProyecto.objects.filter(
                proyecto=proyecto
            ).order_by('-version').first()
            
            nueva_version = 1
            if ultima_version:
                nueva_version = ultima_version.version + 1
            
            # Crear nueva planificación
            planificacion = PlanificacionProyecto.objects.create(
                proyecto=proyecto,
                table_config=table_config,
                rows_data=actividades_data,  # Guardar los datos originales
                version=nueva_version,
                creado_por=usuario
            )
            
            resultados['planificacion_id'] = planificacion.id
            resultados['version'] = planificacion.version
            
            # Registrar cambio general usando los datos proporcionados o creando uno por defecto
            if cambio_planificacion_data:
                # Usar los datos proporcionados desde el frontend
                CambioPlanificacion.objects.create(
                    planificacion=planificacion,
                    tipo_cambio=cambio_planificacion_data.get('tipo_cambio', 'actualizacion'),
                    datos_anteriores=cambio_planificacion_data.get('datos_anteriores', None),
                    datos_nuevos=cambio_planificacion_data.get('datos_nuevos', {
                        'actividades_procesadas': len(actividades_data),
                        'creadas': resultados['creadas'],
                        'actualizadas': resultados['actualizadas'],
                        'errores': len(resultados['errores']),
                        'version_nueva': nueva_version
                    }),
                    descripcion=cambio_planificacion_data.get('descripcion', 
                        f"Planificación {'creada' if not ultima_version else 'actualizada'} v{nueva_version}"),
                    realizado_por=cambio_planificacion_data.get('realizado_por', usuario)
                )
            else:
                # Crear registro por defecto
                CambioPlanificacion.objects.create(
                    planificacion=planificacion,
                    tipo_cambio='actualizacion' if ultima_version else 'creacion',
                    datos_anteriores={
                        'version_anterior': ultima_version.version if ultima_version else None,
                        'total_actividades_anteriores': len(ultima_version.rows_data) if ultima_version else 0
                    },
                    datos_nuevos={
                        'actividades_procesadas': len(actividades_data),
                        'creadas': resultados['creadas'],
                        'actualizadas': resultados['actualizadas'],
                        'errores': len(resultados['errores']),
                        'version_nueva': nueva_version
                    },
                    descripcion=f"Planificación {'creada' if not ultima_version else 'actualizada'} v{nueva_version}",
                    realizado_por=usuario
                )
            
        except Exception as e:
            resultados['errores_planificacion'] = {
                'error': f'Error al guardar la planificación: {str(e)}'
            }
            # Hacer rollback de la transacción si hay error en planificación
            raise e
        
        # Response final
        return Response(resultados, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )