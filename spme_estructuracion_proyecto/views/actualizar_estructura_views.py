# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, DatabaseError
import logging
from spme_estructuracion_proyecto.models import (
    Proyecto, ObjetivoGeneralProyecto, ObjetivoEspecificoProyecto,
    ResultadoOG, ResultadoOE, ProductoOE, ProductoResultadoOE,
    IndicadorObjetivoGeneral, IndicadorObjetivoEspecifico,
    IndicadorResultadoObjGral, IndicadorResultadoObjEspecifico,
    Proceso, ProductoGeneral, DiagramaEstructura
)
from spme_actividades.models import Actividad

# Configurar logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@transaction.atomic
def actualizar_estructura_transaccional(request):
    """
    Endpoint transaccional completo para actualizar estructura desde DiagramaEstructura
    Modo TODO-O-NADA: Si falla cualquier nodo, se hace rollback completo
    """
    try:
        data = request.data
        
        # Validar formato básico
        if 'codigoProyecto' not in data or 'nodos' not in data:
            return Response(
                {'error': 'Formato inválido. Se requieren codigoProyecto y nodos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        codigo_proyecto = data['codigoProyecto']
        nodos = data['nodos']
        conexiones = data.get('conexiones', [])
        diagrama_id = data.get('id')
        
        # Obtener proyecto con LOCK para evitar condiciones de carrera
        try:
            proyecto = Proyecto.objects.select_for_update().get(codigo=codigo_proyecto)
        except Proyecto.DoesNotExist:
            return Response(
                {'error': f'Proyecto con código {codigo_proyecto} no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        resultados = {
            'actualizados': 0,
            'detalles': {},
            'proyecto_id': proyecto.id,
            'proyecto_codigo': proyecto.codigo
        }
        
        # Procesar cada nodo - si alguno falla, la transacción hará rollback automático
        for i, nodo in enumerate(nodos):
            nodo_id = nodo.get('id', f'nodo-{i}')
            tipo = nodo.get('type')
            datos_nodo = nodo.get('data', {}).get('datosNodo', {})
            
            if not datos_nodo:
                continue
            
            # Procesar nodo según su tipo
            resultado = procesar_nodo_transaccional(tipo, datos_nodo, proyecto)
            
            if resultado['success']:
                resultados['actualizados'] += 1
                resultados['detalles'][nodo_id] = {
                    'tipo': tipo,
                    'modelo': resultado['modelo'],
                    'id': resultado['id'],
                    'accion': resultado.get('accion', 'updated')
                }
            else:
                # Cualquier error hace que la transacción falle completamente
                raise DatabaseError(f"Error en nodo {nodo_id}: {resultado['error']}")
        
        # Actualizar el diagrama de estructura
        if diagrama_id:
            # Actualizar diagrama existente
            diagrama = DiagramaEstructura.objects.select_for_update().get(id=diagrama_id)
            diagrama.nodos = nodos
            diagrama.conexiones = conexiones
            diagrama.sincronizado = True
            diagrama.save()
        else:
            # Crear o actualizar diagrama
            diagrama, created = DiagramaEstructura.objects.update_or_create(
                proyecto=proyecto,
                defaults={
                    'codigoProyecto': codigo_proyecto,
                    'nodos': nodos,
                    'conexiones': conexiones,
                    'sincronizado': True
                }
            )
        
        resultados['diagrama_actualizado'] = True
        resultados['diagrama_id'] = diagrama.id
        
        return Response({
            'message': f'Transacción completada exitosamente. {resultados["actualizados"]} nodos actualizados.',
            'resultados': resultados
        }, status=status.HTTP_200_OK)
        
    except Proyecto.DoesNotExist:
        return Response(
            {'error': 'Proyecto no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except DiagramaEstructura.DoesNotExist:
        return Response(
            {'error': 'Diagrama no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except DatabaseError as e:
        # Rollback automático por la transacción
        return Response({
            'error': 'Transacción fallida - Rollback realizado',
            'detalle_error': str(e),
            'tipo_error': 'database_error'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Rollback automático por la transacción
        logger.exception("Error inesperado en transacción")
        return Response({
            'error': 'Error interno - Rollback realizado',
            'detalle_error': str(e),
            'tipo_error': 'internal_error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def procesar_nodo_transaccional(tipo, datos_nodo, proyecto):
    """
    Procesa un nodo individual dentro de la transacción
    """
    try:
        if tipo == 'proyecto':
            return actualizar_proyecto_transaccional(datos_nodo, proyecto)
        elif tipo == 'objetivo_general':
            return actualizar_objetivo_general_transaccional(datos_nodo, proyecto)
        elif tipo == 'objetivo_especifico':
            return actualizar_objetivo_especifico_transaccional(datos_nodo, proyecto)
        elif tipo == 'resultado_og':
            return actualizar_resultado_og_transaccional(datos_nodo, proyecto)
        elif tipo == 'resultado_oe':
            return actualizar_resultado_oe_transaccional(datos_nodo, proyecto)
        elif tipo == 'producto_oe':
            return actualizar_producto_oe_transaccional(datos_nodo, proyecto)
        elif tipo == 'actividad':
            return actualizar_actividad_transaccional(datos_nodo, proyecto)
        else:
            return {
                'success': False,
                'error': f'Tipo de nodo no soportado: {tipo}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error procesando nodo: {str(e)}'
        }

# Funciones transaccionales específicas para cada tipo de modelo
def actualizar_proyecto_transaccional(datos, proyecto):
    """Actualizar proyecto principal con locking"""
    proyecto_id = datos.get('id')
    
    # Verificar que el ID coincide
    if proyecto_id != proyecto.id:
        return {
            'success': False,
            'error': f'ID de proyecto inconsistente: esperado {proyecto.id}, recibido {proyecto_id}'
        }
    
    # Campos actualizables
    campos_actualizables = [
        'codigo', 'titulo', 'descripcion', 'estado', 'presupuesto',
        'fecha_inicio', 'fecha_finalizacion'
    ]
    
    for field in campos_actualizables:
        if field in datos:
            setattr(proyecto, field, datos[field])
    
    proyecto.save()
    
    # Actualizar relaciones ManyToMany
    if 'instancia_gestora' in datos:
        proyecto.instancia_gestora.set(datos['instancia_gestora'])
    if 'procedencia_fondos' in datos:
        proyecto.procedencia_fondos.set(datos['procedencia_fondos'])
    
    return {
        'success': True,
        'modelo': 'Proyecto',
        'id': proyecto.id,
        'accion': 'updated'
    }

def actualizar_objetivo_general_transaccional(datos, proyecto):
    """Actualizar o crear objetivo general con locking"""
    objetivo_id = datos.get('id')
    accion = 'updated'
    
    if objetivo_id:
        objetivo = ObjetivoGeneralProyecto.objects.select_for_update().get(
            id=objetivo_id,
            proyecto=proyecto
        )
    else:
        objetivo = ObjetivoGeneralProyecto(proyecto=proyecto)
        accion = 'created'
    
    # Actualizar campos
    campos = ['codigo', 'descripcion', 'supuestos', 'riesgos']
    for field in campos:
        if field in datos:
            setattr(objetivo, field, datos[field])
    
    objetivo.save()
    
    return {
        'success': True,
        'modelo': 'ObjetivoGeneral',
        'id': objetivo.id,
        'accion': accion
    }

def actualizar_objetivo_especifico_transaccional(datos, proyecto):
    """Actualizar o crear objetivo específico con locking"""
    objetivo_id = datos.get('id')
    accion = 'updated'
    
    if objetivo_id:
        objetivo = ObjetivoEspecificoProyecto.objects.select_for_update().get(
            id=objetivo_id,
            proyecto=proyecto
        )
    else:
        objetivo = ObjetivoEspecificoProyecto(proyecto=proyecto)
        accion = 'created'
    
    # Actualizar campos
    campos = ['codigo', 'descripcion', 'supuestos', 'riesgos']
    for field in campos:
        if field in datos:
            setattr(objetivo, field, datos[field])
    
    # Relación con objetivo general
    if 'objetivo_general' in datos and datos['objetivo_general']:
        try:
            objetivo.objetivo_general = ObjetivoGeneralProyecto.objects.get(
                id=datos['objetivo_general'],
                proyecto=proyecto
            )
        except ObjetivoGeneralProyecto.DoesNotExist:
            pass
    
    objetivo.save()
    
    return {
        'success': True,
        'modelo': 'ObjetivoEspecifico',
        'id': objetivo.id,
        'accion': accion
    }

def actualizar_resultado_og_transaccional(datos, proyecto):
    """Actualizar o crear resultado de objetivo general"""
    resultado_id = datos.get('id')
    accion = 'updated'
    
    if resultado_id:
        resultado = ResultadoOG.objects.select_for_update().get(id=resultado_id)
    else:
        resultado = ResultadoOG()
        accion = 'created'
    
    # Actualizar campos
    campos = ['codigo', 'descripcion', 'supuestos', 'riesgos']
    for field in campos:
        if field in datos:
            setattr(resultado, field, datos[field])
    
    # Relación con objetivo general
    if 'objetivo_general' in datos and datos['objetivo_general']:
        try:
            resultado.objetivo_general = ObjetivoGeneralProyecto.objects.get(
                id=datos['objetivo_general'],
                proyecto=proyecto
            )
        except ObjetivoGeneralProyecto.DoesNotExist:
            pass
    
    resultado.save()
    
    return {
        'success': True,
        'modelo': 'ResultadoOG',
        'id': resultado.id,
        'accion': accion
    }

def actualizar_resultado_oe_transaccional(datos, proyecto):
    """Actualizar o crear resultado de objetivo específico"""
    resultado_id = datos.get('id')
    accion = 'updated'
    
    if resultado_id:
        resultado = ResultadoOE.objects.select_for_update().get(id=resultado_id)
    else:
        resultado = ResultadoOE()
        accion = 'created'
    
    # Actualizar campos
    campos = ['codigo', 'descripcion', 'supuestos', 'riesgos']
    for field in campos:
        if field in datos:
            setattr(resultado, field, datos[field])
    
    # Relación con objetivo específico
    if 'objetivo_especifico' in datos and datos['objetivo_especifico']:
        try:
            resultado.objetivo_especifico = ObjetivoEspecificoProyecto.objects.get(
                id=datos['objetivo_especifico'],
                proyecto=proyecto
            )
        except ObjetivoEspecificoProyecto.DoesNotExist:
            pass
    
    resultado.save()
    
    return {
        'success': True,
        'modelo': 'ResultadoOE',
        'id': resultado.id,
        'accion': accion
    }

def actualizar_producto_oe_transaccional(datos, proyecto):
    """Actualizar o crear producto de objetivo específico"""
    producto_id = datos.get('id')
    accion = 'updated'
    
    if producto_id:
        producto = ProductoOE.objects.select_for_update().get(id=producto_id)
    else:
        producto = ProductoOE()
        accion = 'created'
    
    # Actualizar campos
    campos = ['codigo', 'descripcion', 'supuestos', 'riesgos', 'entregado']
    for field in campos:
        if field in datos:
            setattr(producto, field, datos[field])
    
    # Relación con objetivo específico
    if 'objetivo_especifico' in datos and datos['objetivo_especifico']:
        try:
            producto.objetivo_especifico = ObjetivoEspecificoProyecto.objects.get(
                id=datos['objetivo_especifico'],
                proyecto=proyecto
            )
        except ObjetivoEspecificoProyecto.DoesNotExist:
            pass
    
    producto.save()
    
    return {
        'success': True,
        'modelo': 'ProductoOE',
        'id': producto.id,
        'accion': accion
    }

def actualizar_actividad_transaccional(datos, proyecto):
    """Actualizar o crear actividad con locking"""
    actividad_id = datos.get('id')
    accion = 'updated'
    
    if actividad_id:
        actividad = Actividad.objects.select_for_update().get(
            id=actividad_id,
            proyecto=proyecto
        )
    else:
        actividad = Actividad(proyecto=proyecto)
        accion = 'created'
    
    # Campos básicos
    campos_basicos = [
        'codigo', 'nombreCorto', 'descripcion', 'supuestos', 'riesgos',
        'objetivo_de_actividad', 'descripcion_evaluacion', 'descripcion_tipo_actividad',
        'presupuesto', 'presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo',
        'gradoEjecucion', 'estado', 'procedencia_fondos', 'rutaTrazadoIndicadores',
        'factoresCriticos', 'estructuraProcedencia'
    ]
    
    for field in campos_basicos:
        if field in datos:
            setattr(actividad, field, datos[field])
    
    # Campos de fecha
    for field_fecha in ['fecha_programada', 'fecha_inicio', 'fecha_cierre']:
        if field_fecha in datos:
            setattr(actividad, field_fecha, datos[field_fecha])
    
    actividad.save()
    
    return {
        'success': True,
        'modelo': 'Actividad',
        'id': actividad.id,
        'accion': accion
    }

# Función alternativa para modo tolerante a errores (no transaccional)
@api_view(['POST'])
def actualizar_estructura_tolerante(request):
    """
    Endpoint alternativo que continúa procesando aunque algunos nodos fallen
    """
    try:
        data = request.data
        
        if 'codigoProyecto' not in data or 'nodos' not in data:
            return Response(
                {'error': 'Formato inválido. Se requieren codigoProyecto y nodos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        codigo_proyecto = data['codigoProyecto']
        nodos = data['nodos']
        
        try:
            proyecto = Proyecto.objects.get(codigo=codigo_proyecto)
        except Proyecto.DoesNotExist:
            return Response(
                {'error': f'Proyecto con código {codigo_proyecto} no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        resultados = {
            'actualizados': 0,
            'errores': [],
            'detalles': {}
        }
        
        # Procesar cada nodo individualmente (sin transacción global)
        for i, nodo in enumerate(nodos):
            try:
                with transaction.atomic():
                    nodo_id = nodo.get('id', f'nodo-{i}')
                    tipo = nodo.get('type')
                    datos_nodo = nodo.get('data', {}).get('datosNodo', {})
                    
                    if not datos_nodo:
                        continue
                    
                    resultado = procesar_nodo_transaccional(tipo, datos_nodo, proyecto)
                    
                    if resultado['success']:
                        resultados['actualizados'] += 1
                        resultados['detalles'][nodo_id] = resultado
                    else:
                        resultados['errores'].append({
                            'nodo_id': nodo_id,
                            'error': resultado['error'],
                            'tipo': tipo
                        })
                        
            except Exception as e:
                resultados['errores'].append({
                    'nodo_id': nodo.get('id', f'nodo-{i}'),
                    'error': f'Error en transacción de nodo: {str(e)}',
                    'tipo': tipo
                })
        
        return Response({
            'message': f'Procesamiento completado. {resultados["actualizados"]} nodos actualizados, {len(resultados["errores"])} errores.',
            'resultados': resultados
        }, status=status.HTTP_207_MULTI_STATUS)
        
    except Exception as e:
        return Response({
            'error': f'Error interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)