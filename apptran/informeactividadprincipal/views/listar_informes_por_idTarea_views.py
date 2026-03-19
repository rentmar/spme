# views.py
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from spme_monitoreo.models import InformeTareaPrincipal
from ..serializers.crear_informe_tarea_principal_serializer import InformeTareaPrincipalSerializer

# Endpoint paginado para TAREAS
class InformeTareaPaginadosView(ListAPIView):
    serializer_class = InformeTareaPrincipalSerializer
    
    # Paginación
    class Pagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100
        page_query_param = 'page'
    
    pagination_class = Pagination
    
    def get_queryset(self):
        # ✅ CORREGIDO: Filtrar por tarea_id, no por actividad_id
        return InformeTareaPrincipal.objects.filter(
            tarea_id=self.kwargs['tarea_id'] 
        ).order_by('-fechaEjecucion')

# Endpoint simple para verificar existencia de informe de TAREA
@api_view(['GET'])
def verificar_informe_tarea(request, tarea_id):
    """
    Verifica si existe un informe para una tarea específica
    """
    existe = InformeTareaPrincipal.objects.filter(
        tarea_id=tarea_id  # ← CORREGIDO
    ).exists()
    
    if existe:
        informe = InformeTareaPrincipal.objects.filter(
            tarea_id=tarea_id  # ← CORREGIDO
        ).first()
        
        return Response({
            'existe': True,
            'informe_id': informe.id,
            'numero_informe': informe.numeroInforme,
            'tarea_id': tarea_id
        })
    
    return Response({
        'existe': False,
        'tarea_id': tarea_id
    })