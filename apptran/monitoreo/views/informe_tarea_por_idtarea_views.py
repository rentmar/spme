# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import InfTarea, TareaActividad
from ..serializers.informe_tarea_por_idtarea_serializer import InfTareaSerializer

class InfTareaViewSet(viewsets.ModelViewSet):
    queryset = InfTarea.objects.all()
    serializer_class = InfTareaSerializer
    
    # Endpoint personalizado para obtener informes por ID de tarea
    @action(detail=False, methods=['get'], url_path='por-tarea/(?P<tarea_id>[^/.]+)')
    def por_tarea(self, request, tarea_id=None):
        """
        Obtiene todos los informes de una tarea específica
        """
        try:
            # Verificar que la tarea existe
            tarea = get_object_or_404(TareaActividad, id=tarea_id)
            
            # Obtener todos los informes de esta tarea
            informes = InfTarea.objects.filter(tarea_id=tarea_id)
            
            # Serializar los datos
            serializer = self.get_serializer(informes, many=True)
            
            return Response({
                'success': True,
                'tarea': {
                    'id': tarea.id,
                    'codigo': tarea.codigo,
                    'titulo': tarea.titulo
                },
                'total_informes': informes.count(),
                'informes': serializer.data
            })
            
        except TareaActividad.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Tarea con ID {tarea_id} no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener informes: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)