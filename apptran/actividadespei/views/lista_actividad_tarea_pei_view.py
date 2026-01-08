# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from spme_estructuracion_pei.models import ActividadPei
# from .serializers import ActividadPeiSerializer
from ..serializers.lista_actividad_tarea_pei_serializer import ActividadPeiSerializer

class ActividadesConTareasAPIView(APIView):
    
    def get(self, request):
        try:
            # Queryset base
            actividades = ActividadPei.objects.all()
            
            # Filtros
            estado = request.GET.get('estado')
            if estado:
                actividades = actividades.filter(estado=estado)
            
            responsable_id = request.GET.get('responsable')
            if responsable_id:
                actividades = actividades.filter(responsable_id=responsable_id)
            
            pei_id = request.GET.get('pei')
            if pei_id:
                actividades = actividades.filter(pei_id=pei_id)
            
            tipo_id = request.GET.get('tipo')
            if tipo_id:
                actividades = actividades.filter(tipo_id=tipo_id)
            
            # Búsqueda
            search = request.GET.get('search')
            if search:
                actividades = actividades.filter(
                    models.Q(codigo__icontains=search) |
                    models.Q(nombreCorto__icontains=search) |
                    models.Q(descripcion__icontains=search)
                )
            
            # Ordenación
            ordering = request.GET.get('ordering', '-fecha_programada')
            actividades = actividades.order_by(ordering)
            
            # Optimización
            actividades = actividades.select_related(
                'responsable', 'tipo'  # Solo responsable y tipo, NO pei
            ).prefetch_related(
                'tareas_pei',
                'objetivos_pei',
                'factores_criticos',
                'indicadores_cuantitativos',
                'indicadores_cualitativos'
            )
            
            # Serializar
            serializer = ActividadPeiSerializer(actividades, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )