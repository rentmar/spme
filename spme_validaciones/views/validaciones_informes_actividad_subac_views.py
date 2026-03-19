# spme_validaciones/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError
from ..models import (
    Validacion, 
    ValidacionInformeActividad, 
    ValidacionInformeTarea,
    HistorialValidacion
)
from ..serializers.validaciones_informes_actividad_subac_serializers import (
    ValidacionInformeActividadSerializer,
    ValidacionInformeTareaSerializer,
    AsignarValidadoresSerializer,
    EmitirVotoSerializer,
    HistorialValidacionSerializer,
    EstadoValidacionSerializer
)

# -------------------------------------------------------------------
# VIEWSET PARA VALIDACIONES
# -------------------------------------------------------------------
class ValidacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar validaciones
    
    Endpoints:
    - GET /api/validaciones/           -> Listar mis validaciones
    - GET /api/validaciones/pendientes/ -> Solo pendientes
    - GET /api/validaciones/historial/  -> Ver historial
    - POST /api/validaciones/{id}/votar/ -> Emitir voto
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar validaciones por usuario autenticado"""
        user = self.request.user
        
        # Buscar en ambos tipos de validación
        actividades = ValidacionInformeActividad.objects.filter(
            usuarioValidador=user
        ).select_related(
            'informe', 
            'usuarioValidador', 
            'usuarioRedactor'
        )
        
        tareas = ValidacionInformeTarea.objects.filter(
            usuarioValidador=user
        ).select_related(
            'informeTarea', 
            'usuarioValidador', 
            'usuarioRedactor'
        )
        
        # Combinar y ordenar
        from itertools import chain
        combined = list(chain(actividades, tareas))
        combined.sort(key=lambda x: x.fechaAsignacion, reverse=True)
        return combined
    
    def get_serializer_class(self, instance=None):
        """Selecciona serializer según tipo de instancia"""
        if instance:
            if isinstance(instance, ValidacionInformeActividad):
                return ValidacionInformeActividadSerializer
            elif isinstance(instance, ValidacionInformeTarea):
                return ValidacionInformeTareaSerializer
        return ValidacionInformeActividadSerializer
    
    def list(self, request):
        """Listar todas las validaciones del usuario"""
        queryset = self.get_queryset()
        data = []
        
        for item in queryset:
            if isinstance(item, ValidacionInformeActividad):
                data.append(ValidacionInformeActividadSerializer(item).data)
            else:
                data.append(ValidacionInformeTareaSerializer(item).data)
        
        return Response({
            'count': len(data),
            'results': data
        })
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """
        Listar solo validaciones pendientes del usuario
        GET /api/validaciones/pendientes/
        """
        user = request.user
        
        actividades = ValidacionInformeActividad.objects.filter(
            usuarioValidador=user,
            estado='PENDIENTE'
        ).select_related('informe', 'usuarioRedactor')
        
        tareas = ValidacionInformeTarea.objects.filter(
            usuarioValidador=user,
            estado='PENDIENTE'
        ).select_related('informeTarea', 'usuarioRedactor')
        
        data = []
        for a in actividades:
            data.append(ValidacionInformeActividadSerializer(a).data)
        for t in tareas:
            data.append(ValidacionInformeTareaSerializer(t).data)
        
        # Ordenar por fecha (más reciente primero)
        data.sort(key=lambda x: x['fechaAsignacion'], reverse=True)
        
        return Response({
            'count': len(data),
            'results': data
        })
    
    @action(detail=True, methods=['post'], url_path='(?P<tipo>[^/.]+)/votar') 
    def votar(self, request, pk=None, tipo=None):
        """
        Emitir voto en una validación
    
        POST /api/validaciones/{id}/actividad/votar/
        POST /api/validaciones/{id}/tarea/votar/
        
        Body:
        {
            "estado": "APROBADO",  # o "RECHAZADO"
            "comentarios": "Todo correcto, puede continuar"
        }
        """
        #Validar que el tipo sea correcto
        if tipo not in ['actividad', 'tarea']:
            return Response(
                {'error': 'Tipo debe ser "actividad" o "tarea"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        #Seleccionar el modelo y serializer segun el tipo
        if tipo == 'actividad':
            Modelo = ValidacionInformeActividad
            Serializer = ValidacionInformeActividadSerializer
        elif tipo== 'tarea':
            Modelo = ValidacionInformeTarea
            Serializer = ValidacionInformeTareaSerializer

        # Buscar la validación
        try:
            validacion = Modelo.objects.get(
                id=pk,
                usuarioValidador=request.user,
                estado='PENDIENTE'
            )
        except Modelo.DoesNotExist:
            # Mensaje más específico según el tipo
            return Response(
                {'error': f'Validación de {tipo} no encontrada o ya procesada'},
                status=status.HTTP_404_NOT_FOUND
            ) 

        # Validar datos del voto
        voto_serializer = EmitirVotoSerializer(data=request.data)
        if not voto_serializer.is_valid():
            return Response(voto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Validación adicional: comentarios obligatorios si es RECHAZADO
        if voto_serializer.validated_data['estado'] == 'RECHAZADO' and \
        not voto_serializer.validated_data.get('comentarios'):
            return Response(
                {'error': 'Los comentarios son obligatorios cuando se rechaza'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Actualizar validación
        validacion.estado = voto_serializer.validated_data['estado']
        validacion.comentarios = voto_serializer.validated_data.get('comentarios', '')
        validacion.save()
        
        # Retornar serializer según tipo
        return Response(Serializer(validacion).data)
        
        
            
    @action(detail=False, methods=['get'])
    def historial(self, request):
        """
        Ver historial de cambios
        
        GET /api/validaciones/historial/ 
            -> Historial del usuario (últimos 50)
            
        GET /api/validaciones/historial/?validacion_id=1
            -> Historial de una validación específica
        """
        validacion_id = request.query_params.get('validacion_id')
        
        if validacion_id:
            # Historial de una validación específica
            historial = HistorialValidacion.objects.filter(
                validacion_id=validacion_id
            ).select_related('usuario', 'validacion')
        else:
            # Historial del usuario (como validador o redactor)
            historial = HistorialValidacion.objects.filter(
                Q(usuario=request.user) |
                Q(validacion__usuarioValidador=request.user) |
                Q(validacion__usuarioRedactor=request.user)
            ).select_related('usuario', 'validacion')
        
        serializer = HistorialValidacionSerializer(
            historial.order_by('-fechaCambio')[:50],  # Últimos 50
            many=True
        )
        
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """
        Resumen de validaciones del usuario
        GET /api/validaciones/resumen/
        """
        user = request.user
        
        # Actividades
        act_pendientes = ValidacionInformeActividad.objects.filter(
            usuarioValidador=user, 
            estado='PENDIENTE'
        ).count()
        
        act_aprobadas = ValidacionInformeActividad.objects.filter(
            usuarioValidador=user, 
            estado='APROBADO'
        ).count()
        
        act_rechazadas = ValidacionInformeActividad.objects.filter(
            usuarioValidador=user, 
            estado='RECHAZADO'
        ).count()
        
        # Tareas
        tar_pendientes = ValidacionInformeTarea.objects.filter(
            usuarioValidador=user, 
            estado='PENDIENTE'
        ).count()
        
        tar_aprobadas = ValidacionInformeTarea.objects.filter(
            usuarioValidador=user, 
            estado='APROBADO'
        ).count()
        
        tar_rechazadas = ValidacionInformeTarea.objects.filter(
            usuarioValidador=user, 
            estado='RECHAZADO'
        ).count()
        
        return Response({
            'actividades': {
                'pendientes': act_pendientes,
                'aprobadas': act_aprobadas,
                'rechazadas': act_rechazadas,
                'total': act_pendientes + act_aprobadas + act_rechazadas
            },
            'tareas': {
                'pendientes': tar_pendientes,
                'aprobadas': tar_aprobadas,
                'rechazadas': tar_rechazadas,
                'total': tar_pendientes + tar_aprobadas + tar_rechazadas
            },
            'global': {
                'pendientes': act_pendientes + tar_pendientes,
                'aprobadas': act_aprobadas + tar_aprobadas,
                'rechazadas': act_rechazadas + tar_rechazadas,
                'total': act_pendientes + act_aprobadas + act_rechazadas + tar_pendientes + tar_aprobadas + tar_rechazadas
            }
        })


# -------------------------------------------------------------------
# VIEWSET PARA ASIGNAR VALIDADORES
# -------------------------------------------------------------------
class AsignarValidadoresViewSet(viewsets.ViewSet):
    """
    ViewSet para asignar validadores a documentos
    
    POST /api/asignar-validadores/
    {
        "tipo_documento": "actividad",  # o "tarea"
        "documento_id": 1,
        "validador_ids": [2, 3, 4]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Asignar validadores a un informe"""
        serializer = AsignarValidadoresSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        resultados = []
        errores = []
        
        # Obtener el documento según tipo
        if data['tipo_documento'] == 'actividad':
            from spme_monitoreo.models import InformeActividadPrincipal
            try:
                documento = InformeActividadPrincipal.objects.get(id=data['documento_id'])
                ModeloValidacion = ValidacionInformeActividad
                campo_documento = 'informe'
            except InformeActividadPrincipal.DoesNotExist:
                return Response(
                    {'error': f'Informe de actividad {data["documento_id"]} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:  # tarea
            from spme_monitoreo.models import InformeTareaPrincipal
            try:
                documento = InformeTareaPrincipal.objects.get(id=data['documento_id'])
                ModeloValidacion = ValidacionInformeTarea
                campo_documento = 'informeTarea'
            except InformeTareaPrincipal.DoesNotExist:
                return Response(
                    {'error': f'Informe de tarea {data["documento_id"]} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Obtener usuarios validadores
        from spme_autenticacion.models import Usuario
        validadores = Usuario.objects.filter(id__in=data['validador_ids'])
        
        # Verificar que todos los IDs existen
        if len(validadores) != len(data['validador_ids']):
            ids_encontrados = list(validadores.values_list('id', flat=True))
            ids_faltantes = set(data['validador_ids']) - set(ids_encontrados)
            return Response(
                {'error': f'Validadores no encontrados: {list(ids_faltantes)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear validaciones
        for validador in validadores:
            try:
                # Verificar si ya existe (por si acaso)
                existe = ModeloValidacion.objects.filter(
                    **{campo_documento: documento},
                    usuarioValidador=validador
                ).exists()
                
                if existe:
                    errores.append({
                        'validador_id': validador.id,
                        'error': f'Ya existe una validación para este validador'
                    })
                    continue
                
                # Crear nueva validación
                kwargs = {
                    campo_documento: documento,
                    'usuarioValidador': validador,
                    'usuarioRedactor': request.user,
                    'estado': 'PENDIENTE',
                    'versionDocumento': '1'
                }
                
                validacion = ModeloValidacion.objects.create(**kwargs)
                
                if isinstance(validacion, ValidacionInformeActividad):
                    resultados.append(ValidacionInformeActividadSerializer(validacion).data)
                else:
                    resultados.append(ValidacionInformeTareaSerializer(validacion).data)
                    
            except ValidationError as e:
                errores.append({
                    'validador_id': validador.id,
                    'error': str(e)
                })
            except Exception as e:
                errores.append({
                    'validador_id': validador.id,
                    'error': f'Error inesperado: {str(e)}'
                })
        
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones',
            'errores': errores if errores else None,
            'resultados': resultados
        })


# -------------------------------------------------------------------
# VIEWSET PARA CONSULTAR ESTADO
# -------------------------------------------------------------------
class EstadoValidacionViewSet(viewsets.ViewSet):
    """
    ViewSet para consultar estado de validación de un documento
    
    GET /api/estado-validacion/?tipo=actividad&id=1
    GET /api/estado-validacion/?tipo=tarea&id=1
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Consultar estado consolidado de un documento"""
        tipo = request.query_params.get('tipo')
        documento_id = request.query_params.get('id')
        
        if not tipo or not documento_id:
            return Response(
                {'error': 'Debe especificar tipo e id del documento'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener documento y validaciones según tipo
        if tipo == 'actividad':
            from spme_monitoreo.models import InformeActividadPrincipal
            try:
                documento = InformeActividadPrincipal.objects.get(id=documento_id)
                validaciones = ValidacionInformeActividad.objects.filter(
                    informe=documento
                ).select_related('usuarioValidador')
                serializer_class = ValidacionInformeActividadSerializer
                tipo_doc = 'ACTIVIDAD'
            except InformeActividadPrincipal.DoesNotExist:
                return Response(
                    {'error': f'Informe de actividad {documento_id} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif tipo == 'tarea':
            from spme_monitoreo.models import InformeTareaPrincipal
            try:
                documento = InformeTareaPrincipal.objects.get(id=documento_id)
                validaciones = ValidacionInformeTarea.objects.filter(
                    informeTarea=documento
                ).select_related('usuarioValidador')
                serializer_class = ValidacionInformeTareaSerializer
                tipo_doc = 'TAREA'
            except InformeTareaPrincipal.DoesNotExist:
                return Response(
                    {'error': f'Informe de tarea {documento_id} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Tipo de documento no válido. Use "actividad" o "tarea"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular estado consolidado
        total = validaciones.count()
        pendientes = validaciones.filter(estado='PENDIENTE').count()
        aprobados = validaciones.filter(estado='APROBADO').count()
        rechazados = validaciones.filter(estado='RECHAZADO').count()
        
        if total == 0:
            estado = 'SIN_VALIDACIONES'
        elif rechazados > 0:
            estado = 'RECHAZADO'
        elif pendientes > 0:
            estado = 'EN_VALIDACION'
        elif aprobados == total:
            estado = 'APROBADO'
        else:
            estado = 'PARCIAL'
        
        # Obtener versión actual (la más reciente)
        version_actual = '1'
        if validaciones.exists():
            version_actual = validaciones.first().versionDocumento
        
        # Preparar respuesta
        response_data = {
            'documento_id': documento.id,
            'documento_numero': getattr(documento, 'numeroInforme', ''),
            'tipo_documento': tipo_doc,
            'estado_consolidado': estado,
            'version_actual': version_actual,
            'resumen': {
                'total_validadores': total,
                'pendientes': pendientes,
                'aprobados': aprobados,
                'rechazados': rechazados
            },
            'validaciones': serializer_class(validaciones, many=True).data
        }
        
        return Response(response_data)


# -------------------------------------------------------------------
# VIEWSET PARA RESETEO POR NUEVA VERSIÓN
# -------------------------------------------------------------------
class ResetearValidacionesViewSet(viewsets.ViewSet):
    """
    ViewSet para resetear validaciones cuando hay nueva versión
    
    POST /api/resetear-validaciones/
    {
        "tipo_documento": "actividad",
        "documento_id": 1,
        "nueva_version": "2"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Resetear validaciones a PENDIENTE para nueva versión"""
        tipo = request.data.get('tipo_documento')
        documento_id = request.data.get('documento_id')
        nueva_version = request.data.get('nueva_version', '2')
        
        if not tipo or not documento_id:
            return Response(
                {'error': 'Debe especificar tipo_documento y documento_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener documento y validaciones
        if tipo == 'actividad':
            from spme_monitoreo.models import InformeActividadPrincipal
            try:
                documento = InformeActividadPrincipal.objects.get(id=documento_id)
                validaciones = ValidacionInformeActividad.objects.filter(
                    informe=documento
                )
            except InformeActividadPrincipal.DoesNotExist:
                return Response(
                    {'error': 'Documento no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            from spme_monitoreo.models import InformeTareaPrincipal
            try:
                documento = InformeTareaPrincipal.objects.get(id=documento_id)
                validaciones = ValidacionInformeTarea.objects.filter(
                    informeTarea=documento
                )
            except InformeTareaPrincipal.DoesNotExist:
                return Response(
                    {'error': 'Documento no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Resetear cada validación
        reseteadas = 0
        for v in validaciones:
            if v.estado != 'PENDIENTE':
                v.estado = 'PENDIENTE'
                v.versionDocumento = nueva_version
                v.fechaResolucion = None
                v.save()
                reseteadas += 1
        
        return Response({
            'mensaje': f'Reseteadas {reseteadas} validaciones a versión {nueva_version}',
            'documento_id': documento.id,
            'documento_numero': getattr(documento, 'numeroInforme', ''),
            'nueva_version': nueva_version
        })