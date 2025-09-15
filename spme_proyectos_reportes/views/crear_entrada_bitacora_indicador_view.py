# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spme_estructuracion_proyecto.models import IndicadorProyecto
from ..models import BitacoraIndicador
from ..serializers.crear_entrada_bitacora_indicador_serializer import BitacoraIndicadorCreateSerializer 
#from .models import BitacoraIndicador, IndicadorProyecto
#from .serializers import BitacoraIndicadorCreateSerializer
from spme_estructuracion_proyecto.models import (
    IndicadorProyecto, 
    IndicadorObjetivoGeneral, 
    IndicadorObjetivoEspecifico, 
    IndicadorResultadoObjGral, 
    IndicadorResultadoObjEspecifico)

@api_view(['POST'])
def crear_bitacora_indicador(request):
    serializer = BitacoraIndicadorCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            bitacora = serializer.save()
            
            # Obtener el indicador padre para obtener el tipo
            indicador_padre = bitacora.indicador
            
            # Obtener el ID del modelo hijo basado en el tipo de indicador
            id_hijo = obtener_id_hijo(indicador_padre, serializer.validated_data['tipoIndicador'])
            
            # Preparar respuesta con el formato solicitado
            respuesta = {
                'mensaje': 'Bitácora creada exitosamente',
                'traza': {
                    'id_padre': bitacora.indicador.id,
                    'id_hijo': id_hijo,
                    'tipoIndicador': serializer.validated_data['tipoIndicador'],
                    'observaciones': bitacora.reporteEscrito,
                    'fechaBitacora': bitacora.fechaBitacora.isoformat() if bitacora.fechaBitacora else None,
                    'idBitacora': bitacora.id,
                    'tipo': indicador_padre.tipo if indicador_padre else None
                }
            }
            
            return Response(respuesta, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'mensaje': f'Error al crear la bitácora: {str(e)}',
                'traza': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'mensaje': 'Datos inválidos',
        'errores': serializer.errors,
        'traza': None
    }, status=status.HTTP_400_BAD_REQUEST)

def obtener_id_hijo(indicador_padre, tipo_indicador):
    """
    Obtiene el ID del modelo hijo basado en el tipo de indicador
    """
    try:
        if tipo_indicador == 'indicadorog':
            indicador_hijo = IndicadorObjetivoGeneral.objects.get(indicadorproyecto_ptr=indicador_padre)
            return indicador_hijo.id
        elif tipo_indicador == 'indicadoroe':
            indicador_hijo = IndicadorObjetivoEspecifico.objects.get(indicadorproyecto_ptr=indicador_padre)
            return indicador_hijo.id
        elif tipo_indicador == 'indicadorrog':
            indicador_hijo = IndicadorResultadoObjGral.objects.get(indicadorproyecto_ptr=indicador_padre)
            return indicador_hijo.id
        elif tipo_indicador == 'indicadorroe':
            indicador_hijo = IndicadorResultadoObjEspecifico.objects.get(indicadorproyecto_ptr=indicador_padre)
            return indicador_hijo.id
        return None
    except Exception as e:
        print(f"Error al obtener ID hijo: {str(e)}")
        return None

# Versión alternativa usando relaciones inversas
def obtener_id_hijo_alternativo(indicador_padre, tipo_indicador):
    """
    Obtiene el ID del modelo hijo usando relaciones inversas
    """
    try:
        if tipo_indicador == 'indicadorog' and hasattr(indicador_padre, 'indicadorobjetivogeneral'):
            return indicador_padre.indicadorobjetivogeneral.id
        elif tipo_indicador == 'indicadoroe' and hasattr(indicador_padre, 'indicadorobjetivoespecifico'):
            return indicador_padre.indicadorobjetivoespecifico.id
        elif tipo_indicador == 'indicadorrog' and hasattr(indicador_padre, 'indicadorresultadoobjgral'):
            return indicador_padre.indicadorresultadoobjgral.id
        elif tipo_indicador == 'indicadorroe' and hasattr(indicador_padre, 'indicadorresultadoobjespecifico'):
            return indicador_padre.indicadorresultadoobjespecifico.id
        return None
    except Exception as e:
        print(f"Error al obtener ID hijo (alternativo): {str(e)}")
        return None