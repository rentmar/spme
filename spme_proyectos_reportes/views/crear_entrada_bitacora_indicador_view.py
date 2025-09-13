# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_proyectos_reportes.models import BitacoraIndicador
from ..serializers.crear_entrada_bitacora_indicador_serializer import (
    BitacoraIndicadorCreateSerializer,
    BitacoraIndicadorResponseSerializer
)

class BitacoraIndicadorViewSet(viewsets.ModelViewSet):
    queryset = BitacoraIndicador.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BitacoraIndicadorCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
        except Exception as e:
            return Response(
                {
                    'mensaje_exito': False,
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener datos para la respuesta
        bitacora = serializer.instance
        respuesta_data = {
            'mensaje_exito': True,
            'traza_bitacora': {
                'idindicador_base': bitacora._respuesta_data['idindicador_base'],
                'idindicador_hijo': bitacora._respuesta_data['idindicador_hijo'],
                'tipo_indicador': bitacora._respuesta_data['tipo_indicador_detallado'],
                'tipo_indicador_codigo': bitacora._respuesta_data['tipo_indicador_codigo'],
                'idbitacora': bitacora.id,
                'codigo_indicador': bitacora._respuesta_data['codigo_indicador'],
                'descripcion_indicador': bitacora._respuesta_data['descripcion_indicador'],
                'tipo_dato_indicador': bitacora._respuesta_data['tipo_dato_indicador']
            }
        }
        
        respuesta_serializer = BitacoraIndicadorResponseSerializer(respuesta_data)
        headers = self.get_success_headers(serializer.data)
        return Response(
            respuesta_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['post'], url_path='registrar-masivo')
    def registrar_masivo(self, request):
        """
        Endpoint para registro masivo de bitácoras
        """
        if not isinstance(request.data, list):
            return Response(
                {
                    'mensaje_exito': False,
                    'error': 'Se esperaba una lista de bitácoras'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultados = []
        for index, item_data in enumerate(request.data):
            serializer = BitacoraIndicadorCreateSerializer(data=item_data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    bitacora = serializer.instance
                    resultados.append({
                        'indice': index,
                        'mensaje_exito': True,
                        'traza_bitacora': {
                            'idindicador_base': bitacora._respuesta_data['idindicador_base'],
                            'idindicador_hijo': bitacora._respuesta_data['idindicador_hijo'],
                            'tipo_indicador': bitacora._respuesta_data['tipo_indicador_detallado'],
                            'tipo_indicador_codigo': bitacora._respuesta_data['tipo_indicador_codigo'],
                            'idbitacora': bitacora.id,
                            'codigo_indicador': bitacora._respuesta_data['codigo_indicador'],
                            'descripcion_indicador': bitacora._respuesta_data['descripcion_indicador'],
                            'tipo_dato_indicador': bitacora._respuesta_data['tipo_dato_indicador']
                        }
                    })
                except Exception as e:
                    resultados.append({
                        'indice': index,
                        'mensaje_exito': False,
                        'error': str(e)
                    })
            else:
                resultados.append({
                    'indice': index,
                    'mensaje_exito': False,
                    'error': serializer.errors
                })
        
        return Response({
            'mensaje_exito': any(item['mensaje_exito'] for item in resultados),
            'resultados': resultados
        })