# views.py 
# services/mensajes_papelera_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ..models import MensajeUsuario, EstadoMensaje
from ..serializers.mensajes_papelera_serializer import MensajeUsuarioSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MensajeUsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar mensajes de usuario.
    """
    serializer_class = MensajeUsuarioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['asunto', 'contenido', 'message_id']
    ordering_fields = ['fecha_envio', 'fecha_leido', 'prioridad', 'asunto']
    
    def get_queryset(self):
        """
        Retorna solo los mensajes donde el usuario autenticado
        es el destinatario y no están eliminados por defecto.
        """
        return MensajeUsuario.objects.filter(
            destinatario=self.request.user
        ).exclude(
            estado=EstadoMensaje.ELIMINADO
        )
    
    @action(detail=False, methods=['get'], url_path='eliminados')
    def mensajes_eliminados(self, request):
        """
        Endpoint para obtener todos los mensajes eliminados del usuario.
        
        Parámetros opcionales:
        - tipo: filtrar por tipo de mensaje (privado, sistema, etc.)
        - desde_fecha: filtrar desde fecha específica (YYYY-MM-DD)
        - hasta_fecha: filtrar hasta fecha específica (YYYY-MM-DD)
        - incluir_sistema: boolean para incluir mensajes del sistema (true/false)
        - search: búsqueda en asunto y contenido
        """
        # Obtener parámetros de consulta
        tipo = request.query_params.get('tipo')
        desde_fecha = request.query_params.get('desde_fecha')
        hasta_fecha = request.query_params.get('hasta_fecha')
        incluir_sistema = request.query_params.get('incluir_sistema', 'true').lower() == 'true'
        search_term = request.query_params.get('search', '')
        
        # Base query: mensajes eliminados del usuario
        queryset = MensajeUsuario.objects.filter(
            destinatario=request.user,
            estado=EstadoMensaje.ELIMINADO
        )
        
        # Filtrar por tipo si se especifica
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por rango de fechas
        if desde_fecha:
            queryset = queryset.filter(fecha_envio__date__gte=desde_fecha)
        if hasta_fecha:
            queryset = queryset.filter(fecha_envio__date__lte=hasta_fecha)
        
        # Excluir mensajes del sistema si no se solicitan
        if not incluir_sistema:
            queryset = queryset.exclude(tipo='sistema')
        
        # Búsqueda en asunto y contenido
        if search_term:
            queryset = queryset.filter(
                Q(asunto__icontains=search_term) |
                Q(contenido__icontains=search_term)
            )
        
        # Ordenar por fecha de eliminación (más reciente primero)
        queryset = queryset.order_by('-fecha_actualizacion')
        
        # Paginar resultados
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='restaurar')
    def restaurar_mensaje(self, request, pk=None):
        """
        Endpoint para restaurar un mensaje eliminado.
        Cambia el estado de ELIMINADO a NO_LEIDO.
        """
        try:
            mensaje = MensajeUsuario.objects.get(
                pk=pk,
                destinatario=request.user,
                estado=EstadoMensaje.ELIMINADO
            )
            mensaje.marcar_como_no_leido(commit=True)
            serializer = self.get_serializer(mensaje)
            return Response({
                'status': 'success',
                'message': 'Mensaje restaurado correctamente',
                'data': serializer.data
            })
        except MensajeUsuario.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Mensaje no encontrado o no está eliminado'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], url_path='restaurar-lote')
    def restaurar_lote(self, request):
        """
        Endpoint para restaurar múltiples mensajes eliminados.
        
        Parámetros:
        - ids: lista de IDs de mensajes a restaurar
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'status': 'error',
                'message': 'Se requiere la lista de IDs'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Restaurar mensajes
        mensajes = MensajeUsuario.objects.filter(
            id__in=ids,
            destinatario=request.user,
            estado=EstadoMensaje.ELIMINADO
        )
        
        mensajes_restaurados = []
        for mensaje in mensajes:
            mensaje.marcar_como_leido(commit=True)
            mensajes_restaurados.append(mensaje.id)
        
        return Response({
            'status': 'success',
            'message': f'{len(mensajes_restaurados)} mensajes restaurados',
            'restaurados': mensajes_restaurados,
            'total_solicitados': len(ids)
        })

    @action(detail=False, methods=['delete'], url_path='eliminar-permanentemente')
    def eliminar_permanentemente(self, request):
        """
        Endpoint para eliminar permanentemente mensajes ya marcados como eliminados.
        
        Parámetros:
        - ids: lista de IDs de mensajes a eliminar permanentemente (opcional)
        - eliminar_todos: boolean para eliminar todos los mensajes eliminados
        """
        ids = request.data.get('ids', [])
        eliminar_todos = request.data.get('eliminar_todos', False)
        
        # Obtener mensajes eliminados del usuario
        queryset = MensajeUsuario.objects.filter(
            destinatario=request.user,
            estado=EstadoMensaje.ELIMINADO
        )
        
        # Filtrar por IDs específicos si se proporcionan
        if ids and not eliminar_todos:
            queryset = queryset.filter(id__in=ids)
        
        # Contar antes de eliminar
        total_a_eliminar = queryset.count()
        
        # Eliminar permanentemente
        eliminados, _ = queryset.delete()
        
        return Response({
            'status': 'success',
            'message': f'{eliminados} mensajes eliminados permanentemente',
            'total_eliminados': eliminados
        })