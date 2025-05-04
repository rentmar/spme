#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets

from spme_web.models import Tarea
from .domain.models.response.serializers import TareaSerializer

#Presenter
from .presenters.tareaPresenter import TareaPresenter

# Create your views here.



#Rest Api para Elements
class TareaViewSet(viewsets.ModelViewSet):
    tareas = TareaPresenter()
    queryset = tareas.getTareas()
    #queryset = Tarea.objects.all() #Uso de ORM
    serializer_class = TareaSerializer

