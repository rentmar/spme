from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from spme_proyectos_reportes.models import (
    BitacoraPrincipalIndicadorOg,
    BitacoraPrincipalIndicadorOE,
    BitacoraPrincipalIndicadorRog,
    BitacoraPrincipalIndicadorRoe,
    InformeActividadPrincipal,
    InformeTareaPrincipal,
)
from spme_proyectos_reportes.repositories.bitacora_crud_repository import (
    BitacoraCrudRepository
)
from spme_proyectos_reportes.services.bitacora_crud_service import (
    BitacoraCrudService
)
from spme_proyectos_reportes.serializers.bitacora_crud_serializers import (
    BitacoraCrearSerializer,
    BitacoraActualizarSerializer,
    BitacoraConsultaSerializer,
    BitacoraOGSerializer,
    BitacoraOESerializer,
    BitacoraROGSerializer,
    BitacoraROESerializer,
)


class BitacoraBaseViewSet(viewsets.ViewSet):
    """
    ViewSet base con endpoints CRUD para bitácoras.
    Solo maneja HTTP, delega lógica al servicio.
    """
    permission_classes = [IsAuthenticated]
    
    # Atributos de clase (se sobrescriben en subclases)
    modelo = None
    campo_indicador = None
    serializer_class = None
    
    @property
    def servicio(self):
        """Crea servicio bajo demanda con el modelo y campo correctos"""
        if not hasattr(self, '_servicio'):
            repo = BitacoraCrudRepository(self.modelo)
            self._servicio = BitacoraCrudService(repo, self.campo_indicador)
        return self._servicio
    
    # ─── RESOLVER FK ────────────────────────────────
    
    def _resolver_informe_actividad(self, informe_id):
        """Resuelve FK de informe de actividad"""
        if informe_id:
            try:
                return InformeActividadPrincipal.objects.get(id=informe_id)
            except InformeActividadPrincipal.DoesNotExist:
                pass
        return None
    
    def _resolver_informe_tarea(self, informe_id):
        """Resuelve FK de informe de tarea"""
        if informe_id:
            try:
                return InformeTareaPrincipal.objects.get(id=informe_id)
            except InformeTareaPrincipal.DoesNotExist:
                pass
        return None
    
    # ─── CREAR ──────────────────────────────────────
    
    def create(self, request):
        """POST /api/bitacoras/og/"""
        serializer = BitacoraCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        datos = serializer.validated_data
        
        try:
            entrada = self.servicio.crear(
                usuario_registro=request.user,
                indicador_id=datos.pop('indicador_id'),
                tipo_dato=datos.pop('tipo_dato'),
                valor_literal=datos.pop('valor_literal', None),
                valor_numerico=datos.pop('valor_numerico', None),
                valor_porcentual=datos.pop('valor_porcentual', None),
                fecha_registro=datos.pop('fecha_registro', None),
                observaciones=datos.pop('observaciones', None),
                archivos_adjuntos=datos.pop('archivos_adjuntos', None),
                snapshot_indicador=datos.pop('snapshot_indicador', None),
                informe_actividad=self._resolver_informe_actividad(
                    datos.pop('informe_actividad_id', None)
                ),
                informe_tarea=self._resolver_informe_tarea(
                    datos.pop('informe_tarea_id', None)
                ),
            )
            
            output = self.serializer_class(entrada)
            return Response(output.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
    
    # ─── LISTAR ────────────────────────────────────
    
    def list(self, request):
        """GET /api/bitacoras/og/"""
        entradas = self.servicio.obtener_todos()
        serializer = self.serializer_class(entradas, many=True)
        return Response({
            'count': entradas.count(),
            'results': serializer.data
        })
    
    # ─── DETALLE ───────────────────────────────────
    
    def retrieve(self, request, pk=None):
        """GET /api/bitacoras/og/{id}/"""
        entrada = self.servicio.obtener_por_id(int(pk))
        
        if not entrada:
            return Response(
                {'detail': 'No encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.serializer_class(entrada)
        return Response(serializer.data)
    
    # ─── ACTUALIZAR ────────────────────────────────
    
    def update(self, request, pk=None):
        """PUT /api/bitacoras/og/{id}/"""
        entrada = self.servicio.obtener_por_id(int(pk))
        if not entrada:
            return Response(
                {'detail': 'No encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BitacoraActualizarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        actualizado = self.servicio.actualizar(int(pk), **serializer.validated_data)
        output = self.serializer_class(actualizado)
        return Response(output.data)
    
    def partial_update(self, request, pk=None):
        """PATCH /api/bitacoras/og/{id}/"""
        return self.update(request, pk)
    
    # ─── ELIMINAR ──────────────────────────────────
    
    def destroy(self, request, pk=None):
        """DELETE /api/bitacoras/og/{id}/"""
        eliminado = self.servicio.eliminar(int(pk))
        
        if not eliminado:
            return Response(
                {'detail': 'No encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # ─── CONSULTAR POR FECHAS ──────────────────────
    
    @action(detail=False, methods=['post'])
    def consultar(self, request):
        """
        POST /api/bitacoras/og/consultar/
        Body: {"fecha_inicio": "2026-01-01", "fecha_fin": "2026-12-31", "indicador_id": 1}
        """
        serializer = BitacoraConsultaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        datos = serializer.validated_data
        resultados = self.servicio.consultar(
            indicador_id=datos.get('indicador_id'),
            fecha_inicio=datos['fecha_inicio'],
            fecha_fin=datos['fecha_fin'],
        )
        
        output = self.serializer_class(resultados, many=True)
        return Response({
            'count': resultados.count(),
            'results': output.data
        })
    
    # ─── ÚLTIMO REGISTRO ───────────────────────────
    
    @action(detail=False, methods=['get'])
    def ultimo(self, request):
        """
        GET /api/bitacoras/og/ultimo/?indicador_id=1
        """
        indicador_id = request.query_params.get('indicador_id')
        
        if not indicador_id:
            return Response(
                {'error': 'indicador_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        registro = self.servicio.obtener_ultimo(int(indicador_id))
        
        if not registro:
            return Response(
                {'detail': 'No hay registros para este indicador'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.serializer_class(registro)
        return Response(serializer.data)


# ═══════════════════════════════════════════════════════
# VIEWSETS CONCRETOS
# ═══════════════════════════════════════════════════════

class BitacoraOGViewSet(BitacoraBaseViewSet):
    modelo = BitacoraPrincipalIndicadorOg
    campo_indicador = 'indicador_og_id'
    serializer_class = BitacoraOGSerializer


class BitacoraOEViewSet(BitacoraBaseViewSet):
    modelo = BitacoraPrincipalIndicadorOE
    campo_indicador = 'indicador_oe_id'
    serializer_class = BitacoraOESerializer


class BitacoraROGViewSet(BitacoraBaseViewSet):
    modelo = BitacoraPrincipalIndicadorRog
    campo_indicador = 'indicador_rog_id'
    serializer_class = BitacoraROGSerializer


class BitacoraROEViewSet(BitacoraBaseViewSet):
    modelo = BitacoraPrincipalIndicadorRoe
    campo_indicador = 'indicador_roe_id'
    serializer_class = BitacoraROESerializer