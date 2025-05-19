#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .domain.models.request.libroRequest import LibroRequest
from .domain.models.response.libroResponse import LibroResponse
from rest_framework.response import Response
from rest_framework import status

from .presenters.libroPresenter import LibroPresenter



class getLibro(APIView):
    #POST
    def post(self, request, *args, **kwargs):
	#Request: El serializer es un request	
        libroRequest =  LibroRequest(data=request.data)

        if libroRequest.is_valid():
            libroPresenter = LibroPresenter()
            libro = libroPresenter.getLibro(libroRequest.validated_data)
            # Crear un diccionario con los datos de respuesta
        
            # Pasar los datos al serializer de respuesta
            libroResponse = LibroResponse(libro)
                        
            return Response(libroResponse.data, status=status.HTTP_200_OK)
        return Response(libroRequest.errors, status=status.HTTP_400_BAD_REQUEST)


