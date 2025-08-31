from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from spme_estructuracion_proyecto.models import Proyecto
from .models import ProyectoPlan, PlanRevision
from .serializers import ProyectoPlanSerializer, PlanRevisionSerializer, ProyectoPlanDetailSerializer

class ProyectoPlanViewSet(viewsets.ModelViewSet):
    queryset = ProyectoPlan.objects.all()
    serializer_class = ProyectoPlanSerializer

    def get_queryset(self):
        """Filtra por proyecto_id si viene en la URL"""
        queryset = super().get_queryset()
        proyecto_id = self.request.query_params.get('proyecto_id')
        if proyecto_id:
            queryset = queryset.filter(proyecto_id=proyecto_id)
        return queryset

    @action(detail=True, methods=['post'])
    def create_revision(self, request, pk=None):
        """Endpoint especial para crear revisiones"""
        plan = self.get_object()
        serializer = PlanRevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Calcula la nueva versión
        last_version = plan.revisiones.aggregate(models.Max('version'))['version__max'] or 0
        
        serializer.save(
            plan=plan,
            version=last_version + 1,
            modificado_por=request.user.username if request.user.is_authenticated else 'system'
        )
        
        # Actualiza la versión del plan
        plan.version = last_version + 1
        plan.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PlanRevisionViewSet(viewsets.ModelViewSet):
    serializer_class = PlanRevisionSerializer
    
    def get_queryset(self):
        """Filtra revisiones por plan_id"""
        queryset = PlanRevision.objects.all()
        plan_id = self.request.query_params.get('plan_id')
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
        return queryset
    

class LatestProjectPlanAPIView(APIView):
    """
    Endpoint para obtener la última versión de la planificación de un proyecto
    GET /api/proyectos/{proyectoId}/planificacion/
    """
    def get(self, request, proyectoId):
        try:
            proyecto = Proyecto.objects.get(pk=proyectoId)
            planificacion = ProyectoPlan.objects.filter(
                proyecto=proyecto
            ).order_by('-version').first()
            
            if planificacion:
                serializer = ProyectoPlanSerializer(planificacion)
                return Response({
                    'exists': True,
                    'planificacion': serializer.data
                })
            
            return Response({
                'exists': False,
                'message': 'No existe planificación para este proyecto',
                'proyecto_id': proyectoId
            })
            
        except Proyecto.DoesNotExist:
            return Response(
                {'error': 'Proyecto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        