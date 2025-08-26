from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
#from .models import Actividad, Proceso, ProductoOE, ResultadoOE, ResultadoOG, ObjetivoEspecificoProyecto, ObjetivoGeneralProyecto, Proyecto
from django.db import models
from spme_estructuracion_proyecto.models import Proceso, ProductoOE, ResultadoOE, ResultadoOG, ObjetivoEspecificoProyecto, ObjetivoGeneralProyecto,Proyecto
from spme_actividades.models import Actividad
from rest_framework.views import APIView
from rest_framework.response import Response


@api_view(['GET'])
def ruta_actividad_proyecto(request, actividad_id):
    """
    Endpoint que traza la ruta completa de una actividad hasta el proyecto
    """
    try:
        actividad = Actividad.objects.get(id=actividad_id)
        ruta = trace_ruta_actividad(actividad)
        
        return Response({
            'actividad': {
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombreCorto': actividad.nombreCorto,
                'descripcion': actividad.descripcion
            },
            'ruta_completa': ruta,
            'proyecto_final': ruta[-1] if ruta else None
        })
    
    except Actividad.DoesNotExist:
        return Response({'error': 'Actividad no encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def trace_ruta_actividad(actividad):
    """
    Función que traza la ruta de una actividad hasta el proyecto
    """
    ruta = []
    current_obj = actividad
    
    # Agregar la actividad como primer elemento de la ruta
    ruta.append({
        'tipo': 'Actividad',
        'id': actividad.id,
        'codigo': actividad.codigo,
        'nombre': actividad.nombreCorto
    })
    
    # Intentar seguir diferentes caminos posibles
    caminos = [
        trace_camino_proceso,
        trace_camino_producto_oe,
        trace_camino_resultado_oe,
        trace_camino_resultado_og,
        trace_camino_objetivo_especifico,
        trace_camino_objetivo_general,
        trace_camino_objetivo_pei,
        trace_camino_indicador_pei
    ]
    
    for camino_func in caminos:
        resultado = camino_func(current_obj, ruta)
        if resultado and 'proyecto' in resultado:
            return ruta
    
    return ruta

def trace_camino_proceso(obj, ruta):
    """Sigue el camino a través de Proceso"""
    if hasattr(obj, 'proceso') and obj.proceso:
        proceso = obj.proceso
        ruta.append({
            'tipo': 'Proceso',
            'id': proceso.id,
            'codigo': proceso.codigo,
            'nombre': proceso.titulo
        })
        
        # Desde Proceso puede ir a ResultadoOG, ResultadoOE o ProductoOE
        if proceso.resultado_og:
            return trace_camino_resultado_og(proceso.resultado_og, ruta)
        elif proceso.resultado_oe:
            return trace_camino_resultado_oe(proceso.resultado_oe, ruta)
        elif proceso.producto_oe:
            return trace_camino_producto_oe(proceso.producto_oe, ruta)
    
    return None

def trace_camino_producto_oe(obj, ruta):
    """Sigue el camino a través de ProductoOE"""
    producto_oe = None
    
    if hasattr(obj, 'producto_oe') and obj.producto_oe:
        producto_oe = obj.producto_oe
    elif isinstance(obj, ProductoOE):
        producto_oe = obj
    
    if producto_oe:
        ruta.append({
            'tipo': 'ProductoOE',
            'id': producto_oe.id,
            'codigo': producto_oe.codigo,
            'nombre': producto_oe.descripcion[:100] if producto_oe.descripcion else 'Producto OE'
        })
        
        # ProductoOE -> ObjetivoEspecifico
        if producto_oe.objetivo_especifico:
            return trace_camino_objetivo_especifico(producto_oe.objetivo_especifico, ruta)
    
    return None

def trace_camino_resultado_oe(obj, ruta):
    """Sigue el camino a través de ResultadoOE"""
    resultado_oe = None
    
    if hasattr(obj, 'resultado_oe') and obj.resultado_oe:
        resultado_oe = obj.resultado_oe
    elif isinstance(obj, ResultadoOE):
        resultado_oe = obj
    
    if resultado_oe:
        ruta.append({
            'tipo': 'ResultadoOE',
            'id': resultado_oe.id,
            'codigo': resultado_oe.codigo,
            'nombre': resultado_oe.descripcion[:100] if resultado_oe.descripcion else 'Resultado OE'
        })
        
        # ResultadoOE -> ObjetivoEspecifico
        if resultado_oe.objetivo_especifico:
            return trace_camino_objetivo_especifico(resultado_oe.objetivo_especifico, ruta)
    
    return None

def trace_camino_resultado_og(obj, ruta):
    """Sigue el camino a través de ResultadoOG"""
    resultado_og = None
    
    if hasattr(obj, 'resultado_og') and obj.resultado_og:
        resultado_og = obj.resultado_og
    elif isinstance(obj, ResultadoOG):
        resultado_og = obj
    
    if resultado_og:
        ruta.append({
            'tipo': 'ResultadoOG',
            'id': resultado_og.id,
            'codigo': resultado_og.codigo,
            'nombre': resultado_og.descripcion[:100] if resultado_og.descripcion else 'Resultado OG'
        })
        
        # ResultadoOG -> ObjetivoGeneral
        if resultado_og.objetivo_general:
            return trace_camino_objetivo_general(resultado_og.objetivo_general, ruta)
    
    return None

def trace_camino_objetivo_especifico(obj, ruta):
    """Sigue el camino a través de ObjetivoEspecifico"""
    objetivo_especifico = None
    
    if hasattr(obj, 'objetivo_especifico') and obj.objetivo_especifico:
        objetivo_especifico = obj.objetivo_especifico
    elif isinstance(obj, ObjetivoEspecificoProyecto):
        objetivo_especifico = obj
    
    if objetivo_especifico:
        ruta.append({
            'tipo': 'ObjetivoEspecifico',
            'id': objetivo_especifico.id,
            'codigo': objetivo_especifico.codigo,
            'nombre': objetivo_especifico.descripcion[:100] if objetivo_especifico.descripcion else 'Objetivo Específico'
        })
        
        # ObjetivoEspecifico -> ObjetivoGeneral
        if objetivo_especifico.objetivo_general:
            return trace_camino_objetivo_general(objetivo_especifico.objetivo_general, ruta)
        # O directamente al Proyecto
        elif objetivo_especifico.proyecto:
            return trace_camino_proyecto(objetivo_especifico.proyecto, ruta)
    
    return None

def trace_camino_objetivo_general(obj, ruta):
    """Sigue el camino a través de ObjetivoGeneral"""
    objetivo_general = None
    
    if hasattr(obj, 'objetivo_general') and obj.objetivo_general:
        objetivo_general = obj.objetivo_general
    elif isinstance(obj, ObjetivoGeneralProyecto):
        objetivo_general = obj
    
    if objetivo_general:
        ruta.append({
            'tipo': 'ObjetivoGeneral',
            'id': objetivo_general.id,
            'codigo': objetivo_general.codigo,
            'nombre': objetivo_general.descripcion[:100] if objetivo_general.descripcion else 'Objetivo General'
        })
        
        # ObjetivoGeneral -> Proyecto
        if objetivo_general.proyecto:
            return trace_camino_proyecto(objetivo_general.proyecto, ruta)
    
    return None

def trace_camino_objetivo_pei(obj, ruta):
    """Sigue el camino a través de ObjetivoPEI (si existe esta relación)"""
    if hasattr(obj, 'objetivo_pei') and obj.objetivo_pei:
        objetivo_pei = obj.objetivo_pei
        ruta.append({
            'tipo': 'ObjetivoPEI',
            'id': objetivo_pei.id,
            'codigo': objetivo_pei.codigo,
            'nombre': objetivo_pei.descripcion[:100] if objetivo_pei.descripcion else 'Objetivo PEI'
        })
        # Los objetivos PEI no llevan directamente a proyecto, se termina aquí
        return {'proyecto': None}
    
    return None

def trace_camino_indicador_pei(obj, ruta):
    """Sigue el camino a través de IndicadorPEI (si existe esta relación)"""
    if hasattr(obj, 'indicador_pei') and obj.indicador_pei:
        indicador_pei = obj.indicador_pei
        ruta.append({
            'tipo': 'IndicadorPEI',
            'id': indicador_pei.id,
            'codigo': indicador_pei.codigo,
            'nombre': indicador_pei.descripcion[:100] if indicador_pei.descripcion else 'Indicador PEI'
        })
        # Los indicadores PEI no llevan directamente a proyecto, se termina aquí
        return {'proyecto': None}
    
    return None

def trace_camino_proyecto(proyecto, ruta):
    """Termina el camino en el Proyecto"""
    ruta.append({
        'tipo': 'Proyecto',
        'id': proyecto.id,
        'codigo': proyecto.codigo,
        'nombre': proyecto.titulo,
        'estado': proyecto.estado
    })
    return {'proyecto': proyecto}



# Endpoint para obtener todas las rutas posibles de una actividad
@api_view(['GET'])
def rutas_actividad_indicadores(request, actividad_id):
    """
    Endpoint que muestra todas las rutas posibles de una actividad
    """
    try:
        actividad = Actividad.objects.get(id=actividad_id)
        rutas = []
        
        # Función para obtener indicadores de cada tipo de objeto
        def obtener_indicadores_objeto(obj, tipo_obj):
            indicadores = []
            
            if tipo_obj == 'Proyecto':
                # Indicadores de objetivo general del proyecto
                if hasattr(obj, 'objetivo_general') and obj.objetivo_general:
                    indicadores.extend([
                        {
                            'tipo': 'IndicadorObjetivoGeneral',
                            'id': ind.id,
                            'codigo': ind.codigo,
                            'redaccion': ind.redaccion
                        }
                        for ind in obj.objetivo_general.indicador_og.all()
                    ])
            
            elif tipo_obj == 'ObjetivoGeneral':
                # Indicadores del objetivo general
                indicadores.extend([
                    {
                        'tipo': 'IndicadorObjetivoGeneral',
                        'id': ind.id,
                        'codigo': ind.codigo,
                        'redaccion': ind.redaccion
                    }
                    for ind in obj.indicador_og.all()
                ])
            
            elif tipo_obj == 'ObjetivoEspecifico':
                # Indicadores del objetivo específico
                indicadores.extend([
                    {
                        'tipo': 'IndicadorObjetivoEspecifico',
                        'id': ind.id,
                        'codigo': ind.codigo,
                        'redaccion': ind.redaccion
                    }
                    for ind in obj.indicador_oe.all()
                ])
            
            elif tipo_obj == 'ResultadoOG':
                # Indicadores del resultado OG
                indicadores.extend([
                    {
                        'tipo': 'IndicadorResultadoObjGral',
                        'id': ind.id,
                        'codigo': ind.codigo,
                        'redaccion': ind.redaccion
                    }
                    for ind in obj.indicador_res_og.all()
                ])
            
            elif tipo_obj == 'ResultadoOE':
                # Indicadores del resultado OE
                indicadores.extend([
                    {
                        'tipo': 'IndicadorResultadoObjEspecifico',
                        'id': ind.id,
                        'codigo': ind.codigo,
                        'redaccion': ind.redaccion
                    }
                    for ind in obj.indicador_res_oe.all()
                ])
            
            elif tipo_obj == 'ProductoOE':
                # Los productos OE no tienen indicadores directos, pero pueden estar relacionados con indicadores
                # a través de resultados o objetivos
                pass
            
            elif tipo_obj == 'Proceso':
                # Los procesos no tienen indicadores directos
                pass
            
            elif tipo_obj == 'Actividad':
                # Las actividades pueden tener indicadores PEI
                if hasattr(obj, 'indicador_pei') and obj.indicador_pei:
                    indicadores.append({
                        'tipo': 'IndicadorPei',
                        'id': obj.indicador_pei.id,
                        'codigo': obj.indicador_pei.codigo,
                        'redaccion': obj.indicador_pei.descripcion[:100] if obj.indicador_pei.descripcion else 'Indicador PEI'
                    })
            
            return indicadores
        
        # Función para construir ruta con indicadores
        def construir_ruta_con_indicadores(ruta_base):
            ruta_con_indicadores = []
            
            for punto in ruta_base:
                punto_con_indicadores = punto.copy()
                
                # Obtener el objeto real para buscar indicadores
                objeto = None
                if punto['tipo'] == 'Actividad':
                    objeto = actividad
                elif punto['tipo'] == 'Proceso':
                    try:
                        objeto = Proceso.objects.get(id=punto['id'])
                    except Proceso.DoesNotExist:
                        objeto = None
                elif punto['tipo'] == 'ProductoOE':
                    try:
                        objeto = ProductoOE.objects.get(id=punto['id'])
                    except ProductoOE.DoesNotExist:
                        objeto = None
                elif punto['tipo'] == 'ResultadoOE':
                    try:
                        objeto = ResultadoOE.objects.get(id=punto['id'])
                    except ResultadoOE.DoesNotExist:
                        objeto = None
                elif punto['tipo'] == 'ResultadoOG':
                    try:
                        objeto = ResultadoOG.objects.get(id=punto['id'])
                    except ResultadoOG.DoesNotExist:
                        objeto = None
                elif punto['tipo'] == 'ObjetivoEspecifico':
                    try:
                        objeto = ObjetivoEspecificoProyecto.objects.get(id=punto['id'])
                    except ObjetivoEspecificoProyecto.DoesNotExist:
                        objeto = None
                elif punto['tipo'] == 'ObjetivoGeneral':
                    try:
                        objeto = ObjetivoGeneralProyecto.objects.get(id=punto['id'])
                    except ObjetivoGeneralProyecto.DoesNotExist:
                        objeto = None
                elif punto['tipo'] == 'Proyecto':
                    try:
                        objeto = Proyecto.objects.get(id=punto['id'])
                    except Proyecto.DoesNotExist:
                        objeto = None
                
                # Obtener indicadores si el objeto existe
                if objeto:
                    punto_con_indicadores['indicadores'] = obtener_indicadores_objeto(objeto, punto['tipo'])
                else:
                    punto_con_indicadores['indicadores'] = []
                
                ruta_con_indicadores.append(punto_con_indicadores)
            
            return ruta_con_indicadores
        
        # Probar diferentes caminos iniciales
        if actividad.proceso:
            ruta = [{
                'tipo': 'Actividad',
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombre': actividad.nombreCorto
            }]
            trace_camino_proceso(actividad, ruta)
            if ruta[-1]['tipo'] == 'Proyecto':
                rutas.append({
                    'ruta_label': 'Ruta a través de Proceso',
                    'ruta': construir_ruta_con_indicadores(ruta)
                })
        
        if actividad.producto_oe:
            ruta = [{
                'tipo': 'Actividad',
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombre': actividad.nombreCorto
            }]
            trace_camino_producto_oe(actividad, ruta)
            if ruta[-1]['tipo'] == 'Proyecto':
                rutas.append({
                    'ruta_label': 'Ruta a través de Producto OE',
                    'ruta': construir_ruta_con_indicadores(ruta)
                })
        
        if actividad.resultado_oe:
            ruta = [{
                'tipo': 'Actividad',
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombre': actividad.nombreCorto
            }]
            trace_camino_resultado_oe(actividad, ruta)
            if ruta[-1]['tipo'] == 'Proyecto':
                rutas.append({
                    'ruta_label': 'Ruta a través de Resultado OE',
                    'ruta': construir_ruta_con_indicadores(ruta)
                })
        
        if actividad.resultado_og:
            ruta = [{
                'tipo': 'Actividad',
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombre': actividad.nombreCorto
            }]
            trace_camino_resultado_og(actividad, ruta)
            if ruta[-1]['tipo'] == 'Proyecto':
                rutas.append({
                    'ruta_label': 'Ruta a través de Resultado OG',
                    'ruta': construir_ruta_con_indicadores(ruta)
                })
        
        # Si la actividad está directamente vinculada a un proyecto
        if actividad.proyecto:
            ruta = [{
                'tipo': 'Actividad',
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombre': actividad.nombreCorto
            }, {
                'tipo': 'Proyecto',
                'id': actividad.proyecto.id,
                'codigo': actividad.proyecto.codigo,
                'nombre': actividad.proyecto.titulo
            }]
            rutas.append({
                'ruta_label': 'Ruta directa a Proyecto',
                'ruta': construir_ruta_con_indicadores(ruta)
            })
        
        return Response({
            'actividad': {
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombreCorto': actividad.nombreCorto
            },
            'rutas_posibles': rutas,
            'total_rutas': len(rutas)
        })
    
    except Actividad.DoesNotExist:
        return Response({'error': 'Actividad no encontrada'}, status=404)