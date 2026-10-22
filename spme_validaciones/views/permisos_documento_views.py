# spme/spme_validaciones/views/permisos_documento_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from spme_validaciones.constants import TIPOS_DOCUMENTO
from spme_validaciones.services.permisos_documento_service import calcular_permisos
from spme_validaciones.serializers.permisos_documento_serializers import (
    PermisosDocumentoSerializer, 
)
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService

class DocumentoPermisosView(APIView):
    """
    GET /documentos/<tipo>/<documento_id>/permisos

    Devuelve estado, permisos y revisores de un documento.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, tipo: str, documento_id: int):
        # 1. Resolver configuración del tipo
        config = TIPOS_DOCUMENTO.get(tipo)
        if not config:
            return Response(
                {
                    'error': 'TIPO_DOCUMENTO_INVALIDO',
                    'mensaje': f'El tipo "{tipo}" no es válido',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 2. Verificar existencia del documento (404 real)
        modelo = config['modelo']
        try:
            documento = modelo.objects.get(pk=documento_id)
        except modelo.DoesNotExist:
            return Response(
                {
                    'error': 'DOCUMENTO_NO_ENCONTRADO',
                    'mensaje': f'No existe un documento tipo "{tipo}" con id {documento_id}',
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # 3. Obtener validaciones via repository existente
        repository = config['repository']()
        campo_fk = config['campo_fk']
        validaciones = repository.obtener_por_documento(
            documento_id=documento_id,
            campo_fk=campo_fk,
            select_related=['usuarioValidador', 'usuarioRedactor'],
        )
        
        # 4. Fuente de verdad absoluta: El servicio de consolidacion
        consolidacion_svc = ConsolidacionValidacionService()
        # tipo_solicitud = config.get('tipo_solicitud_key', tipo.upper())
        tipo_solicitud = tipo.upper().replace('-', '_')
        metodo_resolucion = getattr(documento, 'metodo_resolucion', 'DECISORIO')
        # El motor dictamina el estado oficial
        estado_consolidado = consolidacion_svc.consolidar_desde_validaciones(
            tipo_solicitud=tipo_solicitud,
            validaciones=validaciones,
            metodo_resolucion=metodo_resolucion,
        )

        # 5. Calcular permisos
        #permisos = calcular_permisos(documento, request.user, resumen)
        permisos = calcular_permisos(documento, request.user, estado_consolidado, validaciones)

        # 6. Serializar
        serializer = PermisosDocumentoSerializer({
            'documento': documento,
            'permisos': permisos,
            'validaciones': validaciones,
        })

        return Response(serializer.data, status=status.HTTP_200_OK)