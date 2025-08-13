from django.shortcuts import render
from spme_estructuracion_pei.models import *
from spme_estructuracion_proyecto.models import *
from rest_framework import viewsets, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializerpei import *
from .serializerproy import *

from rest_framework import viewsets, generics
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
############################### PEI #######################################
#Endpoitn tipo MODEL: Pei
class PeiViewModel(viewsets.ModelViewSet):
    queryset = Pei.objects.all()
    serializer_class = PeiSerializer


############################  Objetivos PEIs    ############################

class ObjetivosPeiViewModel(viewsets.ModelViewSet):
    queryset = ObjetivoPei.objects.all()
    serializer_class = ObjetivoPeiSerializaer


#Factores criticos
class FactoresCriticosView(viewsets.ModelViewSet):
    queryset = FactoresCriticos.objects.all()
    serializer_class = FactoresCriticosSerializer


############################# INDICADORES PEI ###########################

class IndicadorPeiViewSet(viewsets.ModelViewSet):  # Solo lectura, cambia a ModelViewSet si quieres CRUD
    queryset = IndicadorPeiBase.objects.all()
    serializer_class = IndicadorPeiBaseSerializer

  
    
    def get_queryset(self):
        # Extraer todos los indicadores
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            instance = self.get_object() if self.action == 'retrieve' else None
            if instance:
                if isinstance(instance, IndicadorPeiCuantitativo):
                    return IndicadorPeiCuantitativoSerializer
                elif isinstance(instance, IndicadorPeiCualitativo):
                    return IndicadorPeiCualitativoSerializer
            return super().get_serializer_class()
        return super().get_serializer_class()

class IndicadorPeiCuantitativoViewSet(viewsets.ModelViewSet):
    queryset = IndicadorPeiCuantitativo.objects.all()
    serializer_class = IndicadorPeiCuantitativoSerializer

class IndicadorPeiCualitativoViewSet(viewsets.ModelViewSet):
    queryset = IndicadorPeiCualitativo.objects.all()
    serializer_class = IndicadorPeiCualitativoSerializer    


#Vista para objetivos PEI con indicadores
class PeiObjetivosIndicadoresView(generics.RetrieveAPIView):
    queryset = Pei.objects.all()
    serializer_class = PeiObjetivosSerializer
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)    
    
#Obtener el PEI vigente
@api_view(['GET'])
def obtener_pei_vigente(request):
    try:
        pei_vigente = Pei.objects.get(esta_vigente=True)
        serializer = PeiSerializer(pei_vigente)
        return Response(serializer.data)
    except Pei.DoesNotExist:
        return Response({'error': 'No hay PEI vigente'}, status=404)
    except Pei.MultipleObjectsReturned:
        # En caso de haber múltiples PEIs marcados como vigentes
        peis = Pei.objects.filter(esta_vigente=True).order_by('-fecha_creacion')
        pei_vigente = peis.first()
        # Marcamos los otros como no vigentes
        peis.exclude(id=pei_vigente.id).update(esta_vigente=False)
        serializer = PeiSerializer(pei_vigente)
        return Response(serializer.data)

#Establecer el PEI vigente    
@api_view(['POST'])
def establecer_pei_vigente(request, pei_id):
    try:
        # Primero marcamos todos los PEIs como no vigentes
        Pei.objects.all().update(esta_vigente=False)
        
        # Luego marcamos el PEI seleccionado como vigente
        pei = Pei.objects.get(id=pei_id)
        pei.esta_vigente = True
        pei.save()
        
        serializer = PeiSerializer(pei)
        return Response(serializer.data)
    except Pei.DoesNotExist:
        return Response({'error': 'PEI no encontrado'}, status=404)    

################################ PROYECTO ###########################################
#EndPoint tipo MODEL: Proyecto
class ProyectoViewModel(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoDatosSerializer

#Endpoint tipo MODEL: ObjetivoGeneral
class ProyObjGralViewModel(viewsets.ModelViewSet):
    queryset = ObjetivoGeneralProyecto.objects.all()
    serializer_class = ProyObjGralSer

#Endpoitn tipo Model: Objetivo Especifico
class ProyObjEspViewModel(viewsets.ModelViewSet):
    queryset = ObjetivoEspecificoProyecto.objects.all()
    serializer_class = ProyObjEspSer

#Endpoint tipo Model: Instancia Gestora
class ProyInstGestoraViewModel(viewsets.ModelViewSet):
    queryset = InstanciaGestora.objects.all()
    serializer_class = ProyInsGestSer

#Endpoint tipo Model: Procedencia de Fondos
class ProcedenciaFondosViewmodel(viewsets.ModelViewSet):
    queryset = ProcedenciaFondos.objects.all()
    serializer_class = ProcedenciaFondosSerializer    

#Vista para los proyectos en estado de planificacion
class ProyectoPlanificacionView(generics.ListAPIView):
    serializer_class = ProyectoPlanificacionSerializer
    def get_queryset(self):
        pei_id = self.kwargs['pei_id']
        return Proyecto.objects.filter(estado='EP', pei_id=pei_id).prefetch_related('instancia_gestora').order_by('-fecha_creacion')
    
    def list(self, request, *args, **kwargs):
        queryset =  self.get_queryset()
        serializers = self.get_serializer(queryset, many=True)
        return Response(serializers.data)

#Vista para extraer el objetivo general por id de proyecto
class ObjetivoGeneralPorProyectoView(generics.RetrieveAPIView):
    serializer_class = ProyObjGralSer
    def get(self, request, proyecto_id, *args, **kwargs):
        try:
            objetivo = ObjetivoGeneralProyecto.objects.get(proyecto_id=proyecto_id)
            serializer = self.get_serializer(objetivo)
            return Response(serializer.data)
        except ObjetivoGeneralProyecto.DoesNotExist:
            return Response(
                {"detail": "No se encontró objetivo general para este proyecto."},
                status=status.HTTP_404_NOT_FOUND
            )

#Vista para el diagrama de la estructura de proyectos
class DiagramaEstructuraView(viewsets.ModelViewSet):
    queryset = DiagramaEstructura.objects.all()
    serializer_class = DiagramaEstructuraSer

#Vista: Proyecto - estructura -serializador
class ProyectoEstructuraView(RetrieveAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoEstructuraSer
    lookup_field = 'id'


#Vista: Diagramas - actualizar nodos y edges
class DiagramaEstructuraUpdateView(APIView):
    def patch(self, request, pk):
        return self._actualizar(request, pk)

    def put(self, request, pk):
        return self._actualizar(request, pk)

    def _actualizar(self, request, pk):
        try:
            diagrama = DiagramaEstructura.objects.get(pk=pk)
        except DiagramaEstructura.DoesNotExist:
            return Response({'error': 'Diagrama no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DiagramaEstructuraUpdateSerializer(diagrama, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Diagrama actualizado correctamente'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Vista - Indicador Objetivo General
class IndicadorObjetivoGralViewset(viewsets.ModelViewSet):
    queryset = IndicadorObjetivoGeneral.objects.all()
    serializer_class = IndicadorObjetivoGralSerializer

#Vista - Kpi
class KpiViewSet(viewsets.ModelViewSet):
    queryset = Kpi.objects.all()
    serializer_class = KpiSer

#Vista - Resultado de Objetivo General
class ResultadoObjetivoGeneralViewset(viewsets.ModelViewSet):
    queryset = ResultadoOG.objects.all()
    serializer_class = ResultadoOGSerializaer

#VIsta - Resultado de Objetivo Especifico
class ResultadoObjetivoEspecificoViewset(viewsets.ModelViewSet):
    queryset = ResultadoOE.objects.all()
    serializer_class = ResultadoOESer

#Vista - Producto de Objetivo Especifico
class ProductoOEViewset(viewsets.ModelViewSet):
    queryset = ProductoOE.objects.all()
    serializer_class = ProductoOESer

#Vista - Indicador de Resultado OG
class IndicadorResultadoOgViewset(viewsets.ModelViewSet):
    queryset = IndicadorResultadoObjGral.objects.all()
    serializer_class = IndicadorResultadoObjGralSerializ

#Vista - Indicador de Objetivo Especifico
class IndicadorObjetivoEspecificoViewset(viewsets.ModelViewSet):
    queryset = IndicadorObjetivoEspecifico.objects.all()
    serializer_class = IndicadorObjetivoEspecificoSer

#Vista - Indicador Resultado de Objetivo Especifico
class IndicadorResultadoOEViewset(viewsets.ModelViewSet):
    queryset = IndicadorResultadoObjEspecifico.objects.all()
    serializer_class = IndicadorResultadoOESer

#Vista - Producto Resultado Objetivo Especifico
class ProductoResultadoOEViewset(viewsets.ModelViewSet):
    queryset = ProductoResultadoOE.objects.all()
    serializer_class = ProductoResultadoOESer

#Vista - Producto General
class ProductoGeneralViewset(viewsets.ModelViewSet):
    queryset = ProductoGeneral.objects.all()
    serializer_class = ProductoGeneralSerializer    

#Vista - Proceso
class ProcesoViewset(viewsets.ModelViewSet):
    queryset = Proceso.objects.all()
    serializer_class = ProcesosSerializador    

#Vista - Actividad
class ActividadViewset(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer    

#Vista - Proyecto Estructura Completa
class ProyectoDetalladoView(RetrieveAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoEstructuraSerializer
