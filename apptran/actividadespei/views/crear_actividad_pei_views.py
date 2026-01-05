# views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from django.db import transaction
from spme_estructuracion_pei.models import (
    ActividadPei,
    ObjetivoPei,
    FactoresCriticos,
    IndicadorPeiCualitativo,
    IndicadorPeiCuantitativo

)
from ..serializers.crear_actividad_pei_serializer import ActividadPeiSerializer

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

class ActividadPeiPrincipalViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para manejar actividades PEI (CRUD)
    """
    queryset = ActividadPei.objects.all()
    serializer_class = ActividadPeiSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombreCorto', 'descripcion', 'estado']
    ordering_fields = ['codigo', 'fecha_programada', 'fecha_inicio', 'estado']
    ordering = ['-creado_el']  # Orden por defecto
    
    def get_queryset(self):
        """
        Filtrar actividades según parámetros
        """
        queryset = super().get_queryset()
        
        # Filtrar por PEI
        pei_id = self.request.query_params.get('pei', None)
        if pei_id:
            queryset = queryset.filter(pei_id=pei_id)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por responsable
        responsable_id = self.request.query_params.get('responsable', None)
        if responsable_id:
            queryset = queryset.filter(responsable_id=responsable_id)
        
        # Filtrar por tipo
        tipo_id = self.request.query_params.get('tipo', None)
        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)
        
        return queryset
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Crear una nueva actividad PEI
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
        except Exception as e:
            return Response(
                {'error': str(e), 'detalles': 'Error al crear la actividad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Actualizar completamente una actividad PEI (PUT)
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_update(serializer)
        except Exception as e:
            return Response(
                {'error': str(e), 'detalles': 'Error al actualizar la actividad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.data)
    
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """
        Actualizar parcialmente una actividad PEI (PATCH)
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """
        Guardar la instancia con contexto adicional
        """
        # Aquí puedes agregar lógica adicional, como:
        # - Asignar usuario creador
        # - Generar código automático
        # - Validaciones adicionales
        
        # Ejemplo: Generar código automático si no se proporciona
        data = serializer.validated_data
        if not data.get('codigo'):
            # Generar código automático (ajusta según tu lógica)
            pei_id = data.get('pei').id if data.get('pei') else 0
            count = ActividadPei.objects.filter(pei_id=pei_id).count() + 1
            serializer.validated_data['codigo'] = f'ACT-PEI-{pei_id:03d}-{count:04d}'
        
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Guardar la instancia actualizada
        """
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar una actividad PEI (DELETE)
        """
        instance = self.get_object()
        
        # Validar si se puede eliminar (opcional)
        if instance.estado not in ['CRD', 'PLAN']:
            return Response(
                {'error': 'No se puede eliminar una actividad que no está en estado Creada o Planificada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(
            {'mensaje': 'Actividad eliminada correctamente'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Cambiar el estado de una actividad específica
        """
        instance = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Se requiere el campo "estado"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar transición de estado
        estados_permitidos = ['CRD', 'PLAN', 'RETR', 'REPROG', 'EJEC', 'REP', 'FIN']
        if nuevo_estado not in estados_permitidos:
            return Response(
                {'error': f'Estado no válido. Estados permitidos: {estados_permitidos}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado
        instance.estado = nuevo_estado
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """
        Obtener resumen de actividades por estado
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        resumen = {
            'total': queryset.count(),
            'por_estado': {},
            'por_pei': {}
        }
        
        # Contar por estado
        for estado in ActividadPei.ESTADOS_ACTIVIDAD:
            count = queryset.filter(estado=estado[0]).count()
            resumen['por_estado'][estado[1]] = count
        
        # Contar por PEI
        peis = set(queryset.values_list('pei__titulo', flat=True))
        for pei_titulo in peis:
            if pei_titulo:
                count = queryset.filter(pei__titulo=pei_titulo).count()
                resumen['por_pei'][pei_titulo] = count
        
        return Response(resumen)
    
    @action(detail=True, methods=['get'])
    def relaciones(self, request, pk=None):
        """
        Obtener relaciones detalladas de una actividad
        """
        instance = self.get_object()
        
        datos = {
            'actividad': {
                'id': instance.id,
                'codigo': instance.codigo,
                'nombreCorto': instance.nombreCorto,
                'estado': instance.estado
            },
            'objetivos': list(instance.objetivos_pei.values('id', 'codigo', 'descripcion')),
            'factores_criticos': list(instance.factores_criticos.values('id', 'factor_critico')),
            'indicadores_cuantitativos': list(instance.indicadores_cuantitativos.values('id', 'codigo', 'descripcion')),
            'indicadores_cualitativos': list(instance.indicadores_cualitativos.values('id', 'codigo', 'descripcion'))
        }
        
        return Response(datos)