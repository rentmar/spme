# spme_validaciones/views/peticiones/peticion_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404

from spme_validaciones.models_peticiones import PeticionModificacion
from spme_validaciones.serializers.peticiones.peticion_serializers import (
    PeticionModificacionSerializer,
    PeticionCrearSerializer,
)
from spme_validaciones.services.peticiones.peticion_service import PeticionService


class PeticionListCreateView(APIView):
    """
    GET  /peticiones/         → lista peticiones (filtros opcionales)
    POST /peticiones/         → crea una petición

    Filtros GET:
        ?estado=INICIADA
        ?solicitante=me
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        svc = PeticionService()
        qs = PeticionModificacion.objects.select_related(
            'tipo', 'solicitante', 'resuelto_por'
        ).order_by('-fecha_inicio')

        estado = request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        solicitante = request.query_params.get('solicitante')
        if solicitante == 'me':
            qs = qs.filter(solicitante=request.user)

        serializer = PeticionModificacionSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        entrada = PeticionCrearSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        data = entrada.validated_data

        svc = PeticionService()
        try:
            peticion = svc.crear_peticion(
                tipo_codigo=data['tipo'],
                documento_tipo=data['documento_tipo'],
                documento_id=data['documento_id'],  
                solicitante=request.user,
                justificativo=data['justificativo'],
                payload=data.get('payload') or {},
            )
        except PermissionDenied as e:
            return Response(
                {'error': 'PERMISO_DENEGADO', 'mensaje': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': 'VALIDACION', 'mensaje': e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PeticionModificacionSerializer(peticion).data,
            status=status.HTTP_201_CREATED,
        )


class PeticionDetailView(APIView):
    """
    GET /peticiones/<id>/      → detalle
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, peticion_id):
        peticion = get_object_or_404(PeticionModificacion, pk=peticion_id)
        return Response(PeticionModificacionSerializer(peticion).data)


class PeticionEjecutarView(APIView):
    """
    POST /peticiones/<id>/ejecutar/   → ejecuta la petición
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, peticion_id):
        peticion = get_object_or_404(PeticionModificacion, pk=peticion_id)
        svc = PeticionService()
        try:
            svc.ejecutar(peticion, request.user)
        except PermissionDenied as e:
            return Response(
                {'error': 'PERMISO_DENEGADO', 'mensaje': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': 'VALIDACION', 'mensaje': e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(PeticionModificacionSerializer(peticion).data)


class PeticionAnularView(APIView):
    """
    POST /peticiones/<id>/anular/     → anula la petición
    Body: { "motivo": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, peticion_id):
        peticion = get_object_or_404(PeticionModificacion, pk=peticion_id)
        motivo = request.data.get('motivo', '')

        svc = PeticionService()
        try:
            svc.anular(peticion, request.user, motivo=motivo)
        except PermissionDenied as e:
            return Response(
                {'error': 'PERMISO_DENEGADO', 'mensaje': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': 'VALIDACION', 'mensaje': e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(PeticionModificacionSerializer(peticion).data)


class PeticionPorDocumentoView(APIView):
    """
    GET /documentos/<tipo>/<documento_id>/peticiones/
    Lista las peticiones de un documento.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, tipo: str, documento_id: int):
        from spme_validaciones.constants import TIPOS_DOCUMENTO

        config = TIPOS_DOCUMENTO.get(tipo)
        if not config:
            return Response(
                {'error': 'TIPO_DOCUMENTO_INVALIDO', 'mensaje': f'"{tipo}" no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        modelo = config['modelo']
        documento = modelo.objects.filter(pk=documento_id).first()
        if not documento:
            return Response(
                {'error': 'DOCUMENTO_NO_ENCONTRADO'},
                status=status.HTTP_404_NOT_FOUND,
            )

        svc = PeticionService()
        peticiones = svc.listar_por_documento(documento)
        return Response(
            PeticionModificacionSerializer(peticiones, many=True).data,
            status=status.HTTP_200_OK,
        )