from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from spme_estructuracion_proyecto.models import (
    IndicadorProyecto, 
    IndicadorObjetivoGeneral, 
    IndicadorObjetivoEspecifico, 
    IndicadorResultadoObjGral, 
    IndicadorResultadoObjEspecifico
    )
from ..models import BitacoraIndicador
from ..serializers.obtener_bitacora_indicador_serializer import BitacoraIndicadorSerializer


@api_view(['GET'])
def obtener_bitacoras_indicador(request):
    # Obtener parámetros de la URL
    id_indicador = request.GET.get('idIndicador')
    tipo_indicador = request.GET.get('tipoIndicador')
    
    # Validar parámetros requeridos
    if not id_indicador or not tipo_indicador:
        return Response({
            'mensaje': 'Se requieren los parámetros idIndicador y tipoIndicador',
            'bitacoras': []
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar tipo de indicador
    tipos_validos = ['indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe']
    if tipo_indicador not in tipos_validos:
        return Response({
            'mensaje': f'tipoIndicador debe ser uno de: {tipos_validos}',
            'bitacoras': []
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Mapear tipoIndicador a modelo concreto
        modelo_map = {
            'indicadorog': IndicadorObjetivoGeneral,
            'indicadoroe': IndicadorObjetivoEspecifico,
            'indicadorrog': IndicadorResultadoObjGral,
            'indicadorroe': IndicadorResultadoObjEspecifico
        }
        
        modelo_concreto = modelo_map.get(tipo_indicador)
        
        # Obtener la instancia del modelo concreto
        indicador_hijo = get_object_or_404(modelo_concreto, id=id_indicador)
        
        # Obtener el id del padre (IndicadorProyecto)
        id_padre = indicador_hijo.indicadorproyecto_ptr_id
        
        # Obtener todas las bitácoras del indicador padre, ordenadas por fecha
        bitacoras = BitacoraIndicador.objects.filter(
            indicador_id=id_padre
        ).order_by('fechaBitacora')
        
        # Serializar los datos
        serializer = BitacoraIndicadorSerializer(bitacoras, many=True)
        
        return Response({
            'mensaje': f'Bitácoras encontradas: {bitacoras.count()}',
            'id_padre': id_padre,
            'id_hijo': int(id_indicador),
            'tipo_indicador': tipo_indicador,
            'bitacoras': serializer.data
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response({
            'mensaje': 'idIndicador debe ser un número válido',
            'bitacoras': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'mensaje': f'Error al obtener bitácoras: {str(e)}',
            'bitacoras': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Versión alternativa que incluye información del indicador
@api_view(['GET'])
def obtener_bitacoras_indicador_detallado(request):
    # Obtener parámetros de la URL
    id_indicador = request.GET.get('idIndicador')
    tipo_indicador = request.GET.get('tipoIndicador')
    
    # Validar parámetros requeridos
    if not id_indicador or not tipo_indicador:
        return Response({
            'mensaje': 'Se requieren los parámetros idIndicador y tipoIndicador',
            'bitacoras': []
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Mapear tipoIndicador a modelo concreto
        modelo_map = {
            'indicadorog': IndicadorObjetivoGeneral,
            'indicadoroe': IndicadorObjetivoEspecifico,
            'indicadorrog': IndicadorResultadoObjGral,
            'indicadorroe': IndicadorResultadoObjEspecifico
        }
        
        modelo_concreto = modelo_map.get(tipo_indicador)
        if not modelo_concreto:
            return Response({
                'mensaje': 'Tipo de indicador no válido',
                'bitacoras': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener la instancia del modelo concreto
        indicador_hijo = get_object_or_404(modelo_concreto, id=id_indicador)
        
        # Obtener el id del padre (IndicadorProyecto)
        id_padre = indicador_hijo.indicadorproyecto_ptr_id
        
        # Obtener el indicador padre con toda su información
        indicador_padre = get_object_or_404(IndicadorProyecto, id=id_padre)
        
        # Obtener todas las bitácoras del indicador padre, ordenadas por fecha
        bitacoras = BitacoraIndicador.objects.filter(
            indicador_id=id_padre
        ).order_by('fechaBitacora')
        
        # Serializar los datos
        serializer = BitacoraIndicadorSerializer(bitacoras, many=True)
        
        # Información del indicador
        info_indicador = {
            'id_padre': id_padre,
            'id_hijo': int(id_indicador),
            'codigo': indicador_padre.codigo,
            'descripcion': indicador_padre.descripcion,
            'tipo': indicador_padre.tipo,
            'frecuencia': indicador_padre.frecuencia,
            'baseline': indicador_padre.baseline,
            'tipo_indicador': tipo_indicador
        }
        
        return Response({
            'mensaje': f'Bitácoras encontradas: {bitacoras.count()}',
            'indicador': info_indicador,
            'bitacoras': serializer.data
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response({
            'mensaje': 'idIndicador debe ser un número válido',
            'bitacoras': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'mensaje': f'Error al obtener bitácoras: {str(e)}',
            'bitacoras': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)