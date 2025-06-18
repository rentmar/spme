from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .domain.models.response.listPeiResponse import ListaPeiResponse
from .presenters.obtenerPeiPresenter import ObtenerPeiPresenter
from .domain.models.response.ObjetivoEspecificoResponse import ObjetivoEspecificoResponseList
from spme_estructuracion.container.objeticoEspecificoPresenterContainer import ObjetivoEspecificoPresenterContainer
from common.MessageManager import MessageType

class ObtenerPei(APIView):
    def get(self, request, *args, **kwargs):

        obtenerPeiPresenter = ObtenerPeiPresenter()
        listaPei = obtenerPeiPresenter.listaPei() #deviuelve datos en formato esperado

        listaPeiResponse = ListaPeiResponse(data=listaPei) # vuelve Json
        listaPeiResponse.is_valid(raise_exception=True) # valida el campos Json 
        # Retornar la respuesta
        return Response(listaPeiResponse.data, status=status.HTTP_200_OK)

class ObtenerObjetivoEspecifico(APIView):
    def __init__(self):
        self.contenedor = ObjetivoEspecificoPresenterContainer()
        self.objetivoEspecificoPresenter = self.contenedor.objetivoEspecificoPresenter()

    def get(self, request, *args, **kwargs):

        response = self.objetivoEspecificoPresenter.ObjetivoEspecifico()
       
        objetivoEspecificoResponseLista = ObjetivoEspecificoResponseList(data=response)

        if(objetivoEspecificoResponseLista.is_valid()):
            return Response(objetivoEspecificoResponseLista.data, status=status.HTTP_200_OK)

        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)