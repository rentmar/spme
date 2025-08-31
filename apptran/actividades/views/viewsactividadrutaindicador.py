# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_actividades.models import Actividad
from spme_estructuracion_proyecto.models import *
# from .models import (
#     Actividad, Proceso, ResultadoOG, ResultadoOE, 
#     ObjetivoGeneralProyecto, ObjetivoEspecificoProyecto,
#     Proyecto, IndicadorObjetivoGeneral, IndicadorResultadoObjGral,
#     IndicadorObjetivoEspecifico, IndicadorResultadoObjEspecifico
# )

@api_view(['GET'])
def obtener_ruta_actividad_con_indicadores(request, actividad_id):
    """
    Endpoint que devuelve la ruta completa de una actividad incluyendo
    los indicadores relacionados con cada nodo de la ruta.
    """
    try:
        # Obtener la actividad principal
        actividad_obj = get_object_or_404(Actividad, id=actividad_id)
        
        # Inicializar la estructura de respuesta
        respuesta = {
            "actividad": {
                "id": actividad_obj.id,
                "codigo": actividad_obj.codigo,
                "nombreCorto": actividad_obj.nombreCorto,
                "descripcion": actividad_obj.descripcion
            },
            "ruta_completa": [],
            "proyecto_final": None
        }
        
        # Construir la ruta completa
        ruta_completa = []
        
        # 1. Agregar la actividad actual
        actividad_data = {
            "tipo": "Actividad",
            "id": actividad_obj.id,
            "codigo": actividad_obj.codigo,
            "nombre": actividad_obj.nombreCorto,
            "indicadores": obtener_indicadores_actividad(actividad_obj)
        }
        ruta_completa.append(actividad_data)
        
        # 2. Seguir la ruta según las relaciones
        current_obj = actividad_obj
        max_depth = 10  # Prevenir loops infinitos
        
        while current_obj and max_depth > 0:
            max_depth -= 1
            
            # Buscar el siguiente elemento en la ruta
            next_obj = None
            
            if hasattr(current_obj, 'proceso') and current_obj.proceso:
                # Si la actividad tiene un proceso
                proceso_data = {
                    "tipo": "Proceso",
                    "id": current_obj.proceso.id,
                    "codigo": current_obj.proceso.codigo,
                    "nombre": current_obj.proceso.titulo,
                    "indicadores": obtener_indicadores_proceso(current_obj.proceso)
                }
                ruta_completa.append(proceso_data)
                next_obj = current_obj.proceso
                
            elif hasattr(current_obj, 'resultado_oe') and current_obj.resultado_oe:
                # Si la actividad tiene un resultado OE
                resultado_oe_data = {
                    "tipo": "ResultadoOE",
                    "id": current_obj.resultado_oe.id,
                    "codigo": current_obj.resultado_oe.codigo,
                    "nombre": current_obj.resultado_oe.descripcion,
                    "indicadores": obtener_indicadores_resultado_oe(current_obj.resultado_oe)
                }
                ruta_completa.append(resultado_oe_data)
                next_obj = current_obj.resultado_oe
                
            elif hasattr(current_obj, 'resultado_og') and current_obj.resultado_og:
                # Si la actividad tiene un resultado OG
                resultado_og_data = {
                    "tipo": "ResultadoOG",
                    "id": current_obj.resultado_og.id,
                    "codigo": current_obj.resultado_og.codigo,
                    "nombre": current_obj.resultado_og.descripcion,
                    "indicadores": obtener_indicadores_resultado_og(current_obj.resultado_og)
                }
                ruta_completa.append(resultado_og_data)
                next_obj = current_obj.resultado_og
                
            elif hasattr(current_obj, 'objetivo_especifico') and current_obj.objetivo_especifico:
                # Si tiene objetivo específico
                objetivo_especifico_data = {
                    "tipo": "ObjetivoEspecifico",
                    "id": current_obj.objetivo_especifico.id,
                    "codigo": current_obj.objetivo_especifico.codigo,
                    "nombre": current_obj.objetivo_especifico.descripcion,
                    "indicadores": obtener_indicadores_objetivo_especifico(current_obj.objetivo_especifico)
                }
                ruta_completa.append(objetivo_especifico_data)
                next_obj = current_obj.objetivo_especifico
                
            elif hasattr(current_obj, 'objetivo_general') and current_obj.objetivo_general:
                # Si tiene objetivo general
                objetivo_general_data = {
                    "tipo": "ObjetivoGeneral",
                    "id": current_obj.objetivo_general.id,
                    "codigo": current_obj.objetivo_general.codigo,
                    "nombre": current_obj.objetivo_general.descripcion,
                    "indicadores": obtener_indicadores_objetivo_general(current_obj.objetivo_general)
                }
                ruta_completa.append(objetivo_general_data)
                next_obj = current_obj.objetivo_general
                
            elif hasattr(current_obj, 'proyecto') and current_obj.proyecto:
                # Si tiene proyecto (último elemento)
                proyecto_data = {
                    "tipo": "Proyecto",
                    "id": current_obj.proyecto.id,
                    "codigo": current_obj.proyecto.codigo,
                    "nombre": current_obj.proyecto.titulo,
                    "estado": current_obj.proyecto.estado,
                    "indicadores": obtener_indicadores_proyecto(current_obj.proyecto)
                }
                ruta_completa.append(proyecto_data)
                
                # Guardar el proyecto final
                respuesta["proyecto_final"] = {
                    "tipo": "Proyecto",
                    "id": current_obj.proyecto.id,
                    "codigo": current_obj.proyecto.codigo,
                    "nombre": current_obj.proyecto.titulo,
                    "estado": current_obj.proyecto.estado
                }
                break
                
            # Avanzar al siguiente objeto
            current_obj = next_obj
            
            # Si no hay más objetos relacionados, buscar a través de otras relaciones
            if not current_obj:
                # Intentar otras rutas posibles
                if isinstance(current_obj, Proceso):
                    if current_obj.resultado_og:
                        next_obj = current_obj.resultado_og
                    elif current_obj.resultado_oe:
                        next_obj = current_obj.resultado_oe
                    elif current_obj.producto_oe:
                        next_obj = current_obj.producto_oe
                
                elif isinstance(current_obj, ResultadoOE):
                    if current_obj.objetivo_especifico:
                        next_obj = current_obj.objetivo_especifico
                
                elif isinstance(current_obj, ResultadoOG):
                    if current_obj.objetivo_general:
                        next_obj = current_obj.objetivo_general
                
                elif isinstance(current_obj, ObjetivoEspecificoProyecto):
                    if current_obj.objetivo_general:
                        next_obj = current_obj.objetivo_general
                    elif current_obj.proyecto:
                        next_obj = current_obj.proyecto
                
                elif isinstance(current_obj, ObjetivoGeneralProyecto):
                    if current_obj.proyecto:
                        next_obj = current_obj.proyecto
        
        respuesta["ruta_completa"] = ruta_completa
        return Response(respuesta)
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# Funciones auxiliares para obtener indicadores
def obtener_indicadores_actividad(actividad):
    """Obtener indicadores relacionados con una actividad"""
    # Las actividades pueden tener indicadores a través de varios caminos
    indicadores = []
    
    # Si la actividad tiene un indicador PEI asociado directamente
    if actividad.indicador_pei:
        indicadores.append({
            "id": actividad.indicador_pei.id,
            "nombre": actividad.indicador_pei.nombre if hasattr(actividad.indicador_pei, 'nombre') else actividad.indicador_pei.codigo,
            "descripcion": actividad.indicador_pei.descripcion if hasattr(actividad.indicador_pei, 'descripcion') else "Indicador PEI"
        })
    
    return indicadores


def obtener_indicadores_proceso(proceso):
    """Obtener indicadores relacionados con un proceso"""
    # Los procesos generalmente no tienen indicadores directos,
    # pero pueden heredarlos de sus elementos relacionados
    indicadores = []
    return indicadores


def obtener_indicadores_resultado_oe(resultado_oe):
    """Obtener indicadores de un ResultadoOE"""
    indicadores = []
    
    # Indicadores directos del ResultadoOE
    for indicador in resultado_oe.indicador_res_oe.all():
        indicadores.append({
            "id": indicador.id,
            "nombre": indicador.codigo,
            "descripcion": indicador.redaccion or f"Indicador de {resultado_oe.codigo}"
        })
    
    return indicadores


def obtener_indicadores_resultado_og(resultado_og):
    """Obtener indicadores de un ResultadoOG"""
    indicadores = []
    
    # Indicadores directos del ResultadoOG
    for indicador in resultado_og.indicador_res_og.all():
        indicadores.append({
            "id": indicador.id,
            "nombre": indicador.codigo,
            "descripcion": indicador.redaccion or f"Indicador de {resultado_og.codigo}"
        })
    
    return indicadores


def obtener_indicadores_objetivo_especifico(objetivo_especifico):
    """Obtener indicadores de un ObjetivoEspecifico"""
    indicadores = []
    
    # Indicadores directos del ObjetivoEspecifico
    for indicador in objetivo_especifico.indicador_oe.all():
        indicadores.append({
            "id": indicador.id,
            "nombre": indicador.codigo,
            "descripcion": indicador.redaccion or f"Indicador de {objetivo_especifico.codigo}"
        })
    
    return indicadores


def obtener_indicadores_objetivo_general(objetivo_general):
    """Obtener indicadores de un ObjetivoGeneral"""
    indicadores = []
    
    # Indicadores directos del ObjetivoGeneral
    for indicador in objetivo_general.indicador_og.all():
        indicadores.append({
            "id": indicador.id,
            "nombre": indicador.codigo,
            "descripcion": indicador.redaccion or f"Indicador de {objetivo_general.codigo}"
        })
    
    return indicadores


def obtener_indicadores_proyecto(proyecto):
    """Obtener indicadores de un Proyecto"""
    indicadores = []
    
    # Recopilar indicadores de todos los objetivos generales del proyecto
    if hasattr(proyecto, 'objetivo_general'):
        indicadores.extend(obtener_indicadores_objetivo_general(proyecto.objetivo_general))
    
    # Recopilar indicadores de todos los objetivos específicos del proyecto
    for objetivo_especifico in proyecto.objetivos_especificos.all():
        indicadores.extend(obtener_indicadores_objetivo_especifico(objetivo_especifico))
    
    return indicadores