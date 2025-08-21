from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import *
from .serializers import *
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


###################################ENDPOINT DE PRUEBA ##############
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


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

############################## PROYECTOS POR ESTADO #####################################3

#Proyectos por estado
class ProyectosPlanificacionList(generics.ListAPIView):
    serializer_class = ProyectoSerializer
    
    def get_queryset(self):
        # Filtra los proyectos con estado 'EP' (En Planificación)
        return Proyecto.objects.filter(estado='EP')    



###############################  ESTRUCTURA DEL PEI   ########################################33
class PeiEstructuraCompletaView(generics.RetrieveAPIView):
    queryset = Pei.objects.all()
    serializer_class = PeiEstructuraSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'PEI': serializer.data
        })


#############################  CONTEOS DE NODOS  ##########################################

@api_view(['GET'])
def conteos_proyecto(request, proyecto_id):
    try:
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        
        conteos = {
            # Objetivo General y sus elementos
            'objetivo_general': 0,
            'kpi_objetivo_general': 0,
            'indicador_objetivo_general': 0,
            'producto_objetivo_general': 0,
            'indicador_producto_objetivo_general': 0,
            
            # Resultados del Objetivo General y sus elementos
            'resultado_objetivo_general': 0,
            'indicador_resultado_objetivo_general': 0,
            'proceso_resultado_objetivo_general': 0,
            'actividad_resultado_objetivo_general': 0,
            
            # Objetivos Específicos del Objetivo General y sus elementos
            'objetivo_especifico_og': 0,
            'indicador_objetivo_especifico_og': 0,
            'resultado_objetivo_especifico_og': 0,
            'indicador_resultado_objetivo_especifico_og': 0,
            'producto_objetivo_especifico_og': 0,
            'proceso_producto_objetivo_especifico_og': 0,
            'actividad_producto_objetivo_especifico_og': 0,
            
            # Objetivos Específicos directos del Proyecto
            'objetivo_especifico_proyecto': 0,
            'indicador_objetivo_especifico_proyecto': 0,
            'producto_objetivo_especifico_proyecto': 0,
            'indicador_producto_objetivo_especifico_proyecto': 0,
            'resultado_objetivo_especifico_proyecto': 0,
            'indicador_resultado_objetivo_especifico_proyecto': 0
        }
        
        # Obtener el objetivo general del proyecto
        objetivo_general = ObjetivoGeneralProyecto.objects.filter(proyecto=proyecto).first()
        
        if objetivo_general:
            conteos['objetivo_general'] = 1
            
            # KPIs del objetivo general
            conteos['kpi_objetivo_general'] = Kpi.objects.filter(
                objetivo_general=objetivo_general
            ).count()
            
            # Indicadores del objetivo general
            conteos['indicador_objetivo_general'] = IndicadorObjetivoGeneral.objects.filter(
                objetivo_general=objetivo_general
            ).count()
            
            # Productos generales del objetivo general
            conteos['producto_objetivo_general'] = ProductoGeneral.objects.filter(
                objetivo_general=objetivo_general
            ).count()
            
            # Indicadores de productos generales
            conteos['indicador_producto_objetivo_general'] = IndicadorObjetivoGeneral.objects.filter(
                productos_gral_indicador_og__objetivo_general=objetivo_general
            ).count()
            
            # Resultados del objetivo general
            resultados_og = ResultadoOG.objects.filter(objetivo_general=objetivo_general)
            conteos['resultado_objetivo_general'] = resultados_og.count()
            
            # Indicadores de resultados del objetivo general
            conteos['indicador_resultado_objetivo_general'] = IndicadorResultadoObjGral.objects.filter(
                resultado_og__in=resultados_og
            ).count()
            
            # Procesos de resultados del objetivo general
            conteos['proceso_resultado_objetivo_general'] = Proceso.objects.filter(
                resultado_og__in=resultados_og
            ).count()
            
            # Actividades de resultados del objetivo general
            conteos['actividad_resultado_objetivo_general'] = Actividad.objects.filter(
                resultado_og__in=resultados_og
            ).count()
            
            # Objetivos específicos del objetivo general
            objetivos_especificos_og = ObjetivoEspecificoProyecto.objects.filter(
                objetivo_general=objetivo_general
            )
            conteos['objetivo_especifico_og'] = objetivos_especificos_og.count()
            
            if objetivos_especificos_og.exists():
                # Indicadores de objetivos específicos del objetivo general
                conteos['indicador_objetivo_especifico_og'] = IndicadorObjetivoEspecifico.objects.filter(
                    objetivo_especifico__in=objetivos_especificos_og
                ).count()
                
                # Resultados de objetivos específicos del objetivo general
                conteos['resultado_objetivo_especifico_og'] = ResultadoOE.objects.filter(
                    objetivo_especifico__in=objetivos_especificos_og
                ).count()
                
                # Indicadores de resultados de objetivos específicos del objetivo general
                conteos['indicador_resultado_objetivo_especifico_og'] = IndicadorResultadoObjEspecifico.objects.filter(
                    resultado_obj_especifico__objetivo_especifico__in=objetivos_especificos_og
                ).count()
                
                # Productos de objetivos específicos del objetivo general
                conteos['producto_objetivo_especifico_og'] = ProductoOE.objects.filter(
                    objetivo_especifico__in=objetivos_especificos_og
                ).count()
                
                # Procesos de productos de objetivos específicos del objetivo general
                conteos['proceso_producto_objetivo_especifico_og'] = Proceso.objects.filter(
                    producto_oe__objetivo_especifico__in=objetivos_especificos_og
                ).count()
                
                # Actividades de productos de objetivos específicos del objetivo general
                conteos['actividad_producto_objetivo_especifico_og'] = Actividad.objects.filter(
                    producto_oe__objetivo_especifico__in=objetivos_especificos_og
                ).count()
        
        # Objetivos específicos directos del proyecto (no del objetivo general)
        objetivos_especificos_proyecto = ObjetivoEspecificoProyecto.objects.filter(
            proyecto=proyecto,
            objetivo_general__isnull=True  # Solo objetivos específicos no vinculados al objetivo general
        )
        conteos['objetivo_especifico_proyecto'] = objetivos_especificos_proyecto.count()
        
        if objetivos_especificos_proyecto.exists():
            # Indicadores de objetivos específicos directos del proyecto
            conteos['indicador_objetivo_especifico_proyecto'] = IndicadorObjetivoEspecifico.objects.filter(
                objetivo_especifico__in=objetivos_especificos_proyecto
            ).count()
            
            # Productos de objetivos específicos directos del proyecto
            conteos['producto_objetivo_especifico_proyecto'] = ProductoOE.objects.filter(
                objetivo_especifico__in=objetivos_especificos_proyecto
            ).count()
            
            # Indicadores de productos de objetivos específicos directos del proyecto
            conteos['indicador_producto_objetivo_especifico_proyecto'] = IndicadorObjetivoEspecifico.objects.filter(
                productos_gral_indicador_oe__objetivo_especifico__in=objetivos_especificos_proyecto
            ).count()
            
            # Resultados de objetivos específicos directos del proyecto
            conteos['resultado_objetivo_especifico_proyecto'] = ResultadoOE.objects.filter(
                objetivo_especifico__in=objetivos_especificos_proyecto
            ).count()
            
            # Indicadores de resultados de objetivos específicos directos del proyecto
            conteos['indicador_resultado_objetivo_especifico_proyecto'] = IndicadorResultadoObjEspecifico.objects.filter(
                resultado_obj_especifico__objetivo_especifico__in=objetivos_especificos_proyecto
            ).count()
        
        serializer = ConteosProyectoSerializer(conteos)
        return Response(serializer.data)
    
    except Proyecto.DoesNotExist:
        return Response({'error': 'Proyecto no encontrado'}, status=404)


#################### Procesos por Proyecto ############################

class ProcesosPorProyectoListView(generics.ListAPIView):
    serializer_class = ProcesoProyectoSerializer

    def get_queryset(self):
        proyecto_id = self.kwargs['proyecto_id']
        
        # Verifica primero si el proyecto existe
        #from .models import Proyecto
        from spme_estructuracion_proyecto.models import Proyecto
        if not Proyecto.objects.filter(id=proyecto_id).exists():
            return Proceso.objects.none()
        
        # Query optimizado
        return Proceso.objects.filter(
            Q(resultado_og__objetivo_general__proyecto_id=proyecto_id) |
            Q(resultado_oe__objetivo_especifico__proyecto_id=proyecto_id) |
            Q(producto_oe__objetivo_especifico__proyecto_id=proyecto_id)
        ).distinct().order_by('id')

##################3 LISTA DE OBJETIVOS PEI MINIMALISTA #########################3333

class SimpleObjetivosPeiListView(generics.ListAPIView):
    serializer_class = SimpleObjetivoPeiSerializer

    def get_queryset(self):
        return ObjetivoPei.objects.filter(pei_id=self.kwargs['pei_id'])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data
        })


########################## LISTA DE INDICADORES PEI MINIMALISTA   ##################


class IndicadoresCompactosView(APIView):
    """
    Endpoint: /api/objetivos/<id>/indicadores-compactos/
    Devuelve: {"data": ["id-codigo-descripcion", ...]}
    """
    
    def get(self, request, objetivo_id):
        # Verifica que el objetivo exista (devuelve 404 si no)
        objetivo = get_object_or_404(ObjetivoPei, pk=objetivo_id)
        
        # Obtiene solo los campos necesarios para el dropdown
        indicadores = IndicadorPeiBase.objects.filter(
            objetivo_id=objetivo_id
        ).only('id', 'codigo', 'descripcion')
        
        # Formato compacto para el dropdown
        data = [
            f"{ind.id}-{ind.codigo}-{ind.descripcion}"
            for ind in indicadores
            if ind.codigo  # Filtra indicadores sin código
        ]
        
        return Response({"data": data})

################   Indicadores Objetivo General #############333
class IndicadoresObjetivoGeneralView(APIView):
    """
    Endpoint: /api/proyectos/<proyecto_id>/indicadores-og/
    Devuelve los indicadores del objetivo general de un proyecto
    Formato: {"data": ["id-codigo-redaccion", ...]}
    """
    
    def get(self, request, proyecto_id):
        # Verificar que el proyecto existe
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        
        # Obtener el objetivo general del proyecto
        objetivo_general = proyecto.objetivo_general
        if not objetivo_general:
            return Response({
                "success": False,
                "message": "El proyecto no tiene objetivo general definido"
            }, status=404)
        
        # Obtener los indicadores relacionados
        indicadores = IndicadorObjetivoGeneral.objects.filter(
            objetivo_general=objetivo_general
        ).order_by('codigo')
        
        # Formatear la respuesta
        data = [
            f"{ind.id}-{ind.codigo}-{ind.redaccion}"
            for ind in indicadores
            if ind.codigo and ind.redaccion  # Solo si tiene código y redacción
        ]
        
        return Response({
            "success": True,
            "data": data,
            "meta": {
                "proyecto": proyecto.codigo,
                "objetivo_general": objetivo_general.codigo,
                "total_indicadores": len(data)
            }
        })

###################  Objetivo Especifico  #############

class ObjetivosEspecificosCombinadosView(APIView):
    """
    Endpoint: /api/proyectos/<proyecto_id>/objetivos-especificos/
    Devuelve: {
        "data": {
            "proyecto": [lista de objetivos específicos del proyecto],
            "objetivo_general": [lista de objetivos específicos del objetivo general]
        }
    }
    Formato: {"id-codigo-descripcion"}
    """
    
    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        
        # 1. Objetivos específicos directamente del proyecto
        objetivos_proyecto = ObjetivoEspecificoProyecto.objects.filter(
            proyecto=proyecto
        ).order_by('codigo')
        
        # 2. Objetivos específicos del objetivo general del proyecto
        objetivos_general = ObjetivoEspecificoProyecto.objects.none()
        if proyecto.objetivo_general:
            objetivos_general = ObjetivoEspecificoProyecto.objects.filter(
                objetivo_general=proyecto.objetivo_general
            ).order_by('codigo')
        
        # Función para formatear la respuesta
        def formato_objetivo(obj):
            return f"{obj.id}-{obj.codigo}-{obj.descripcion}"
        
        return Response({
            "success": True,
            "data": {
                "proyecto": [formato_objetivo(obj) for obj in objetivos_proyecto],
                "objetivo_general": [formato_objetivo(obj) for obj in objetivos_general]
            },
            "meta": {
                "proyecto": proyecto.codigo,
                "objetivo_general": proyecto.objetivo_general.codigo if proyecto.objetivo_general else None,
                "total_proyecto": objetivos_proyecto.count(),
                "total_objetivo_general": objetivos_general.count()
            }
        })

##########################3 Indicadores OE

@api_view(['GET'])
def indicadores_objetivo_especifico(request, objetivo_id):
    try:
        objetivo = ObjetivoEspecificoProyecto.objects.get(pk=objetivo_id)
        indicadores = objetivo.indicador_oe.all()
        serializer = IndicadorOeCompactoSerializer(indicadores, many=True)
        
        # Extraemos solo los valores 'display'
        data = [item['display'] for item in serializer.data]
        
        return Response({
            "success": True,
            "data": data,
            "count": len(data)
        })
        
    except ObjetivoEspecificoProyecto.DoesNotExist:
        return Response({
            "success": False,
            "message": "Objetivo no encontrado"
        }, status=status.HTTP_404_NOT_FOUND)

####################### PRODUCTOS OBJETIVO ESPECIFICO #########################33
def productos_objetivo_especifico(request, oe_id):
    try:
        objetivo = ObjetivoEspecificoProyecto.objects.get(pk=oe_id)
        productos = ProductoOE.objects.filter(
            objetivo_especifico=objetivo
        ).only('id', 'codigo', 'descripcion')
        
        data = [
            f"{prod.id}-{prod.codigo or ''}-{prod.descripcion or ''}".rstrip('-')
            for prod in productos
        ]
        
        return JsonResponse({"success": True, "data": data})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)
    
########################### RESULTADO OBJETIVO ESPECIFICO  ######################################

def resultados_objetivo_especifico(request, oe_id):
    """
    Endpoint que devuelve los resultados de un objetivo específico
    Formato: ["id-codigo-descripcion", ...]
    """
    try:
        # 1. Verificar que el objetivo existe
        objetivo = ObjetivoEspecificoProyecto.objects.get(pk=oe_id)
        
        # 2. Obtener los resultados relacionados
        resultados = ResultadoOE.objects.filter(
            objetivo_especifico=objetivo
        ).only('id', 'codigo', 'descripcion')
        
        # 3. Formatear la respuesta
        data = [
            f"{res.id}-{res.codigo or ''}-{res.descripcion or ''}".rstrip('-')
            for res in resultados
        ]
        
        return JsonResponse({
            "success": True,
            "data": data,
            "count": len(data),
            "objetivo": {
                "id": objetivo.id,
                "codigo": objetivo.codigo
            }
        })
        
    except ObjetivoEspecificoProyecto.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Objetivo específico no encontrado"
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Error del servidor: {str(e)}"
        }, status=500)

def indicadores_resultado_oe(request, resultado_id):
    """
    Endpoint que devuelve los indicadores de un resultado OE
    Formato: ["id-codigo-redaccion", ...]
    """
    try:
        # 1. Verificar que el resultado existe
        resultado = ResultadoOE.objects.get(pk=resultado_id)
        
        # 2. Obtener los indicadores relacionados
        indicadores = IndicadorResultadoObjEspecifico.objects.filter(
            resultado_obj_especifico=resultado
        ).only('id', 'codigo', 'redaccion')
        
        # 3. Formatear la respuesta
        data = [
            f"{ind.id}-{ind.codigo or ''}-{ind.redaccion or ''}".rstrip('-')
            for ind in indicadores
        ]
        
        return JsonResponse({
            "success": True,
            "data": data,
            "count": len(data)
        })
        
    except ResultadoOE.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Resultado no encontrado"
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Error del servidor: {str(e)}"
        }, status=500)


############################### Actividades ###########################################

class ActividadesProyectoDropdownList(generics.ListAPIView):
    serializer_class = ActividadDropdownSerializer

    def get_queryset(self):
        proyecto_id = self.kwargs['proyecto_id']
        return Actividad.objects.filter(
            Q(proceso__resultado_og__objetivo_general__proyecto_id=proyecto_id) |
            Q(proceso__resultado_oe__objetivo_especifico__proyecto_id=proyecto_id) |
            Q(proceso__producto_oe__objetivo_especifico__proyecto_id=proyecto_id) |
            Q(resultado_og__objetivo_general__proyecto_id=proyecto_id) |
            Q(resultado_oe__objetivo_especifico__proyecto_id=proyecto_id) |
            Q(producto_oe__objetivo_especifico__proyecto_id=proyecto_id)
        ).distinct()


############################   Resultados Objetivo General #####################################3

class ResultadosOGDropdownList(generics.ListAPIView):
    def get(self, request, proyecto_id):
        try:
            # Obtener el objetivo general del proyecto
            objetivo_general = ObjetivoGeneralProyecto.objects.get(proyecto_id=proyecto_id)
            
            # Obtener todos los resultados asociados a ese objetivo general
            resultados = ResultadoOG.objects.filter(objetivo_general=objetivo_general)
            
            # Formatear la respuesta
            data = [{
                'id': resultado.id,
                'codigo': resultado.codigo,
                'descripcion': resultado.descripcion,
                'display_text': f"{resultado.id} - {resultado.codigo} - {resultado.descripcion[:50]}..."
            } for resultado in resultados]
            
            return Response({
                'success': True,
                'data': data
            })
            
        except ObjetivoGeneralProyecto.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontró el objetivo general para este proyecto'
            }, status=404)

class IndicadoresResultadoOGDropdownList(generics.ListAPIView):
    def get(self, request, resultado_og_id):
        try:
            # Obtener todos los indicadores asociados a este resultado OG
            indicadores = IndicadorResultadoObjGral.objects.filter(resultado_og_id=resultado_og_id)
            
            # Formatear la respuesta
            data = [{
                'id': indicador.id,
                'codigo': indicador.codigo,
                'redaccion': indicador.redaccion,
                'display_text': f"{indicador.id} - {indicador.codigo} - {indicador.redaccion[:50]}..."
            } for indicador in indicadores]
            
            return Response({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=400)

######## CONTEOS #################
@api_view(['GET'])
def count_indicadores_og(request, proyecto_id):
    """
    Retorna el conteo de indicadores de objetivo general para un proyecto
    Ejemplo de respuesta: {"count": 3}
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    count = IndicadorObjetivoGeneral.objects.filter(
        objetivo_general__proyecto=proyecto
    ).count()
    
    return Response({"count": count})


@api_view(['GET'])
def count_resultados_og(request, proyecto_id):
    """
    Retorna el conteo de resultados de objetivo general para un proyecto
    Ejemplo de respuesta: {"count": 2}
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    count = ResultadoOG.objects.filter(
        objetivo_general__proyecto=proyecto
    ).count()
    
    return Response({"count": count})

######## CONTEOS FIN  ############

class ColumnVisibilityStatsView(APIView):
    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        objetivo_general = getattr(proyecto, 'objetivo_general', None)
       
        return Response({
            'indicadores_pei': IndicadorPeiBase.objects.filter(objetivo__pei=proyecto.pei).count(),
            'indicadores_og': IndicadorObjetivoGeneral.objects.filter(objetivo_general__proyecto=proyecto).count(),
            'resultados_og': ResultadoOG.objects.filter(objetivo_general__proyecto=proyecto).count(),
            'objetivos_especificos': ObjetivoEspecificoProyecto.objects.filter(
                 Q(proyecto=proyecto) | Q(objetivo_general__proyecto=proyecto)
             ).distinct().count(),
            # Anterior Consulta
            # 'objetivos_especificos': ObjetivoEspecificoProyecto.objects.filter(
            #     Q(proyecto=proyecto) | Q(objetivo_general__proyecto=objetivo_general)
            # ).distinct().count(),
            #'indicadores_oe': IndicadorObjetivoEspecifico.objects.filter(objetivo_especifico__proyecto=proyecto).count(),
            'indicadores_oe': IndicadorObjetivoEspecifico.objects.filter(
                Q(objetivo_especifico__proyecto_id=proyecto_id)|
                Q(objetivo_especifico__objetivo_general__proyecto_id=proyecto_id)
            ).count(),
            #'resultados_oe': ResultadoOE.objects.filter(objetivo_especifico__proyecto=proyecto).count(),
            'resultados_oe': ResultadoOE.objects.filter(
                Q(objetivo_especifico__proyecto_id=proyecto_id)|
                Q(objetivo_especifico__objetivo_general__proyecto_id=proyecto_id)
            ).distinct().count(),
            #'productos_oe': ProductoOE.objects.filter(objetivo_especifico__proyecto=proyecto).count(),
            'productos_oe': ProductoOE.objects.filter(
                Q(objetivo_especifico__proyecto_id=proyecto_id)|
                Q(objetivo_especifico__objetivo_general__proyecto_id=proyecto_id)
            ).count(),
            'tiene_instancias_gestoras': proyecto.instancia_gestora.exists(),
            'tiene_procedencia_fondos': proyecto.procedencia_fondos.exists()
        })





"""
class IndicadorNumericoViewSet(viewsets.ModelViewSet):
    queryset = IndicadorNumerico.objects.all()
    serializer_class = IndicadorNumericoSerializer

class IndicadorLiteralViewSet(viewsets.ModelViewSet):
    queryset = IndicadorLiteral.objects.all()
    serializer_class = IndicadorLiteralSerializer

class IndicadorPorcentualViewSet(viewsets.ModelViewSet):
    queryset = IndicadorPorcentual.objects.all()
    serializer_class = IndicadorPorcentualSerializer
 """
#Endpoint compuesto 
#proyecto   - obj gral
#           - obj espec
""" class ProyectoDetalleView(RetrieveAPIView):
    queryset = Proyecto.objects.select_related('objetivo_general') \
                             .prefetch_related('objetivos_especificos') \
                             .all()
    serializer_class = ProyectosObjetivosSer
    lookup_field = 'pk'
 """
#Endpoint compuesto 
#proyecto   - obj gral  - indicadores de obj general
#                       - relacion a un obj especifico 
#                        - relacion a un resultado - indicadores
#                       -                           - actividades
"""
class ProyectoObjGeneralView(RetrieveAPIView):
    queryset = Proyecto.objects.select_related('objetivo_general').all()
    serializer_class = ProyectoObjGeneralInfoSer
    lookup_field = 'pk'
"""
""" class ProyectoCompletoView(viewsets.ReadOnlyModelViewSet):
    queryset = Proyecto.objects.prefetch_related(
        'objetivos_generales__indicadores_literales',
        'objetivos_generales__indicadores_numericos',
        'objetivos_generales__indicadores_porcentuales'
    )
    queryset = Proyecto.objects.select_related('objetivo_general').prefetch_related(
        'objetivo_general__indicadores_literales',
        'objetivo_general__indicadores_numericos',
        'objetivo_general__indicadores_porcentuales'
    )
    serializer_class = ProyectoCompletoObjGralSerializer

 """
###############OBJETIVOS ESPECIFICOS ######


""" class ObjetivoEspecificoProyectoViewSet(viewsets.ModelViewSet):
    queryset = ObjetivoEspecificoProyecto.objects.all()
    serializer_class = ObjetivoEspecificoProyectoSerializer

class IndicadorObjEspecProyViewSet(viewsets.ModelViewSet):
    queryset = IndicadorObjEspecProy.objects.all()
    serializer_class = IndicadorObjEspecProySerializer

class ResultadoObjEspProyViewSet(viewsets.ModelViewSet):
    queryset = ResultadoObjEspProy.objects.all()
    serializer_class = ResultadoObjEspProySerializer

class IndicadorResultadoProyViewSet(viewsets.ModelViewSet):
    queryset = IndicadorResultadoProy.objects.all()
    serializer_class = IndicadorResultadoProySerializer

class ActividadBaseResultadoViewSet(viewsets.ModelViewSet):
    queryset = ActividadBaseResultado.objects.all()
    serializer_class = ActividadBaseResultadoSerializer

class LineaAccionResultadoViewSet(viewsets.ModelViewSet):
    queryset = LineaAccionResultado.objects.all()
    serializer_class = LineaAccionResultadoSerializer

class ProyectoCompletoDetailView(RetrieveAPIView):
    queryset = Proyecto.objects.all().prefetch_related(
        'objetivos_especificos__indicador_objespec',
        'objetivos_especificos__resultados_objesp__indicador_resultado',
        'objetivos_especificos__resultados_objesp__actividad_result',
        'objetivos_especificos__resultados_objesp__lineaaccion_result',
    )
    serializer_class = ProyectoCompletoSerializer
    lookup_field = 'id'  # o 'pk' si prefieres

 """########################  ################################


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def test_endpoint(request):
    if request.method == 'GET':
        return Response(
            {"message": "Este es un GET de prueba", "data": None},
            status=status.HTTP_200_OK
        )
    
    elif request.method == 'POST':
        return Response(
            {"message": "POST recibido", "data": request.data},
            status=status.HTTP_201_CREATED
        )
    
    elif request.method == 'PUT':
        return Response(
            {"message": "PUT recibido", "data": request.data},
            status=status.HTTP_200_OK
        )
    
    elif request.method == 'DELETE':
        return Response(
            {"message": "DELETE recibido"},
            status=status.HTTP_204_NO_CONTENT
        )