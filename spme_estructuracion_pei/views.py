from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .common.MessageManager import MessageType
from .domain.models.request.estructuracionPeiRequest import CrearEstructuraPEIRequest
from .domain.models.response.estructuracionPeiResponse import CreateEstructuraPeiResponse
from .container.presenterContainer import EstructuracionPeiPresenterContainer

class CrearEstructuraPEI(APIView):
    """
    API Creacion estructura PEI
    """
    def __init__(self):
        self.contenedor = EstructuracionPeiPresenterContainer()
        self.estructuracionPeiPresenter = self.contenedor.estructuracionPeiPresenter() 

    def post(self, request, *args, **kwargs):

        request = CrearEstructuraPEIRequest(data = request.data) 

        if (request.is_valid()):

            createEstructuraPeiResponse = self.estructuracionPeiPresenter.createEstructuraPei(request.validated_data)

            response = CreateEstructuraPeiResponse(data=createEstructuraPeiResponse)

            if (response.is_valid()):
                return Response(response.data,status=status.HTTP_201_CREATED)
            else:
                return Response({"mensaje": MessageType.ERROR.value}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)