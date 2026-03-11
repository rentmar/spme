# views.py (completo con import del serializador)
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from spme_monitoreo.models import InformeActividadPrincipal
from ..serializers.listar_informes_por_idActividad_serializer import InformeActividadPrincipalSerializer

# Endpoint paginado
class InformesActividadPaginadosView(ListAPIView):
    serializer_class = InformeActividadPrincipalSerializer 
    # Paginación personalizada
    class Pagination(PageNumberPagination):
        page_size = 10  # tamaño por defecto
        page_size_query_param = 'page_size'  # parámetro para cambiar tamaño
        max_page_size = 100  # tamaño máximo permitido
        page_query_param = 'page'  # parámetro para página
        
    pagination_class = Pagination
    
    def get_queryset(self):
        return InformeActividadPrincipal.objects.filter(
            actividad_id=self.kwargs['actividad_id']
        ).order_by('-fechaEjecucion')

# Endpoint simple (no necesita serializador)
@api_view(['GET'])
def verificar_informe_actividad(request, actividad_id):
    existe = InformeActividadPrincipal.objects.filter(
        actividad_id=actividad_id
    ).exists()
    
    if existe:
        informe = InformeActividadPrincipal.objects.filter(
            actividad_id=actividad_id
        ).first()
        
        return Response({
            'existe': True,
            'informe_id': informe.id,
            'numero_informe': informe.numeroInforme
        })
    
    return Response({'existe': False})