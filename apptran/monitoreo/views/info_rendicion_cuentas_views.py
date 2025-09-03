from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spme_monitoreo.models import SolicitudFondos
from ..serializers.info_rendicion_cuentas_serializer import SolicitudFondosSerializers

class RendicionCuentasDatosView(APIView):
    """ Endpoint para poblar el formulario Rendicion de cuentas
    POST 
    {
        idsolfondos: 1,
    }
    """
    def post(self, request, *args, **kwargs):
        idSolicitudFondos = request.data.get('idsolfondos')
        #Validar el dato 
        if idSolicitudFondos is None:
            return Response(
                {},
                status=status.HTTP_400_BAD_REQUEST
            )
        #Obtetener el objeto solicitud de fondos
        try:
            solicitudFondos = SolicitudFondos.objects.get(pk=idSolicitudFondos)
        except SolicitudFondos.DoesNotExist:
            return Response(
                {"error": f"Solicitud de Fondos con ID {idSolicitudFondos} no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        #Serializar el objeto para enviarlo 
        serializerSolFond = SolicitudFondosSerializers(solicitudFondos)    
        #Enviar respuesta exitosa
        return Response(
            {
                "mensaje": "correcto",
                "solicitud-fondos": serializerSolFond.data,
            }, status=status.HTTP_200_OK
        )
