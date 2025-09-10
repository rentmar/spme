# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from spme_estructuracion_proyecto.models import *
from ..serializers.estructura_jerarquica_proy_serializer import EstructuraJerarquicaSerializer

@api_view(['GET'])
def estructura_jerarquica_completa(request, proyecto_id):
    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado"}, status=404)
    
    # Estructura base del proyecto
    estructura = {
        "proyecto": {
            "id": proyecto.id,
            "codigo": proyecto.codigo,
            "titulo": proyecto.titulo,
            "descripcion": proyecto.descripcion,
            "objetivo_general": None,
            "objetivos_especificos": []
        }
    }
    
    # Obtener objetivo general si existe
    try:
        objetivo_general = ObjetivoGeneralProyecto.objects.get(proyecto=proyecto)
        estructura["proyecto"]["objetivo_general"] = {
            "id": objetivo_general.id,
            "codigo": objetivo_general.codigo,
            "descripcion": objetivo_general.descripcion,
            "indicadores_og": [],
            "resultados_og": []
        }
        
        # Obtener indicadores del objetivo general
        indicadores_og = IndicadorObjetivoGeneral.objects.filter(objetivo_general=objetivo_general)
        for indicador in indicadores_og:
            estructura["proyecto"]["objetivo_general"]["indicadores_og"].append({
                "id": indicador.id,
                "codigo": indicador.codigo,
                "descripcion": indicador.descripcion,
                "redaccion": indicador.redaccion
            })
        
        # Obtener resultados del objetivo general
        resultados_og = ResultadoOG.objects.filter(objetivo_general=objetivo_general)
        for resultado in resultados_og:
            resultado_data = {
                "id": resultado.id,
                "codigo": resultado.codigo,
                "descripcion": resultado.descripcion,
                "indicadores_rog": []
            }
            
            # Obtener indicadores del resultado OG
            indicadores_res_og = IndicadorResultadoObjGral.objects.filter(resultado_og=resultado)
            for indicador in indicadores_res_og:
                resultado_data["indicadores_rog"].append({
                    "id": indicador.id,
                    "codigo": indicador.codigo,
                    "descripcion": indicador.descripcion,
                    "redaccion": indicador.redaccion
                })
            
            estructura["proyecto"]["objetivo_general"]["resultados_og"].append(resultado_data)
            
    except ObjetivoGeneralProyecto.DoesNotExist:
        pass
    
    # Obtener objetivos específicos RELACIONADOS CON EL OBJETIVO GENERAL
    if estructura["proyecto"]["objetivo_general"]:
        objetivo_general_id = estructura["proyecto"]["objetivo_general"]["id"]
        objetivos_especificos = ObjetivoEspecificoProyecto.objects.filter(
            objetivo_general_id=objetivo_general_id
        )
    else:
        # Fallback: si no hay objetivo general, buscar por proyecto
        objetivos_especificos = ObjetivoEspecificoProyecto.objects.filter(proyecto=proyecto)
    
    for objetivo_especifico in objetivos_especificos:
        objetivo_data = {
            "id": objetivo_especifico.id,
            "codigo": objetivo_especifico.codigo,
            "descripcion": objetivo_especifico.descripcion,
            "indicadores_oe": [],
            "resultados_oe": []
        }
        
        # Obtener indicadores del objetivo específico
        indicadores_oe = IndicadorObjetivoEspecifico.objects.filter(objetivo_especifico=objetivo_especifico)
        for indicador in indicadores_oe:
            objetivo_data["indicadores_oe"].append({
                "id": indicador.id,
                "codigo": indicador.codigo,
                "descripcion": indicador.descripcion,
                "redaccion": indicador.redaccion
            })
        
        # Obtener resultados del objetivo específico
        resultados_oe = ResultadoOE.objects.filter(objetivo_especifico=objetivo_especifico)
        for resultado in resultados_oe:
            resultado_data = {
                "id": resultado.id,
                "codigo": resultado.codigo,
                "descripcion": resultado.descripcion,
                "indicadores_roe": [],
                "productos_roe": []
            }
            
            # Obtener indicadores del resultado OE
            indicadores_res_oe = IndicadorResultadoObjEspecifico.objects.filter(resultado_obj_especifico=resultado)
            for indicador in indicadores_res_oe:
                resultado_data["indicadores_roe"].append({
                    "id": indicador.id,
                    "codigo": indicador.codigo,
                    "descripcion": indicador.descripcion,
                    "redaccion": indicador.redaccion
                })
            
            # Obtener productos del resultado OE
            productos_res_oe = ProductoResultadoOE.objects.filter(resultado_oe=resultado)
            for producto in productos_res_oe:
                resultado_data["productos_roe"].append({
                    "id": producto.id,
                    "codigo": producto.codigo,
                    "descripcion": producto.descripcion
                })
            
            objetivo_data["resultados_oe"].append(resultado_data)
        
        estructura["proyecto"]["objetivos_especificos"].append(objetivo_data)
    
    return Response(estructura)

@api_view(['GET'])
def prueba_conexion_reportes(request):
    """
    Endpoint de prueba para verificar la conexión al módulo de reportes
    """
    return Response({
        'success': True,
        'message': 'exito conexion reportes',
        'status': 'conexion_establecida',
    }, status=status.HTTP_200_OK)