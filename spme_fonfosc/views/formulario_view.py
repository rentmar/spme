# spme/spme_fonfosc/views/formulario_view.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from spme_fonfosc.services.formulario_service import FormularioService
from spme_fonfosc.serializers.formulario_serializer import FormularioSerializer
from spme_fonfosc.models.formulario import Formulario


class FormularioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para formularios.
    
    Endpoints:
    - GET    /api/formularios/                    → Listar todos
    - POST   /api/formularios/                    → Crear nuevo
    - GET    /api/formularios/{id}/               → Obtener uno
    - PUT    /api/formularios/{id}/               → Actualizar completo
    - PATCH  /api/formularios/{id}/               → Actualizar parcial
    - DELETE /api/formularios/{id}/               → Eliminar
    - GET    /api/formularios/mis_formularios/    → Mis formularios
    - GET    /api/formularios/por_estado/         → Filtrar por estado
    - POST   /api/formularios/{id}/publicar/      → Publicar
    - POST   /api/formularios/{id}/archivar/      → Archivar
    - POST   /api/formularios/{id}/duplicar/      → Duplicar
    - POST   /api/formularios/{id}/nueva_version/ → Nueva versión
    """
    
    serializer_class = FormularioSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.formulario_service = FormularioService()
    
    def get_queryset(self):
        """Filtra según permisos del usuario"""
        user = self.request.user
        
        if not user or user.is_anonymous:
            return Formulario.objects.none()
        
        if user.is_staff or user.is_superuser:
            return Formulario.objects.all()
        
        return Formulario.objects.filter(creado_por=user)
    
    def perform_create(self, serializer):
        """Asigna el usuario creador automáticamente"""
        serializer.save(creado_por=self.request.user)
    
    # ============ CRUD BÁSICO ============
    
    def list(self, request):
        """GET /api/formularios/"""
        formularios = self.formulario_service.list_formularios(request.user)
        serializer = self.serializer_class(formularios, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """POST /api/formularios/"""
        try:
            formulario = self.formulario_service.create_formulario(
                request.data,
                request.user
            )
            serializer = self.serializer_class(formulario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def retrieve(self, request, pk=None):
        """GET /api/formularios/{id}/"""
        formulario = self.formulario_service.get_formulario(int(pk))
        
        if not formulario:
            return Response(
                {'error': 'Formulario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.serializer_class(formulario)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """PUT /api/formularios/{id}/"""
        try:
            formulario = self.formulario_service.update_formulario(
                int(pk),
                request.data
            )
            serializer = self.serializer_class(formulario)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def partial_update(self, request, pk=None):
        """PATCH /api/formularios/{id}/"""
        try:
            formulario = self.formulario_service.update_formulario(
                int(pk),
                request.data
            )
            serializer = self.serializer_class(formulario)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, pk=None):
        """DELETE /api/formularios/{id}/"""
        try:
            self.formulario_service.delete_formulario(int(pk))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ============ ENDPOINTS ESPECIALES ============
    
    @action(detail=False, methods=['get'], url_path='mis_formularios')
    def mis_formularios(self, request):
        """GET /api/formularios/mis_formularios/"""
        formularios = self.formulario_service.list_formularios_by_usuario(request.user)
        serializer = self.serializer_class(formularios, many=True)
        return Response({
            'count': len(formularios),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='por_estado')
    def por_estado(self, request):
        """GET /api/formularios/por_estado/?estado=draft"""
        estado = request.query_params.get('estado', '')
        formularios = self.formulario_service.list_formularios_by_estado(estado)
        serializer = self.serializer_class(formularios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='publicar')
    def publicar(self, request, pk=None):
        """POST /api/formularios/{id}/publicar/"""
        try:
            formulario = self.formulario_service.publicar_formulario(int(pk))
            serializer = self.serializer_class(formulario)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='archivar')
    def archivar(self, request, pk=None):
        """POST /api/formularios/{id}/archivar/"""
        try:
            formulario = self.formulario_service.archivar_formulario(int(pk))
            serializer = self.serializer_class(formulario)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='duplicar')
    def duplicar(self, request, pk=None):
        """POST /api/formularios/{id}/duplicar/"""
        try:
            formulario = self.formulario_service.duplicar_formulario(
                int(pk),
                request.user
            )
            serializer = self.serializer_class(formulario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='nueva_version')
    def nueva_version(self, request, pk=None):
        """POST /api/formularios/{id}/nueva_version/"""
        try:
            formulario = self.formulario_service.crear_nueva_version(
                int(pk),
                request.user
            )
            serializer = self.serializer_class(formulario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )