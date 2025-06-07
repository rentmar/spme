from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .domain.models.response.listPeiResponse import ListaPeiResponse, PeiResponse
from .presenters.obtenerPeiPresenter import ObtenerPeiPresenter

class ObtenerPei(APIView):
    def get(self, request, *args, **kwargs):

        obtenerPeiPresenter = ObtenerPeiPresenter()
        listaPei = obtenerPeiPresenter.listaPei() #deviuelve datos en formato esperado

        listaPeiResponse = ListaPeiResponse(data=listaPei) # vuelve Json
        listaPeiResponse.is_valid(raise_exception=True) # valida el campos Json 
        # Retornar la respuesta
        return Response(listaPeiResponse.data, status=status.HTTP_200_OK)
