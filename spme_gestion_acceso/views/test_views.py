#spme_gestion_acceso/views/test_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class TestConnectionView(APIView):
    "Endpoint de prueba"
    def get(self, request, *args, **kwargs):
        mensaje = "Conexion exitosa"

        return Response(
            {"message": mensaje},
            status=status.HTTP_200_OK  
        )