from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class TestConexionView(APIView):
    """
    Enpoint de prueba
    """
    def get(self, request, *args, **kwargs):
        mensaje = "Conexion exitosa al API de impresiones"
        return Response(
            {"message": mensaje},
            status=status.HTTP_200_OK
        )