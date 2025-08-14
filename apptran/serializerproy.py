from rest_framework import serializers
from spme_estructuracion_proyecto.models import *
from spme_actividades.models import *

############################# PROYECTO #######################################
##MODELOS
#Serializador Model Proyecto
class ProyectoDatosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = '__all__'

    def create(self, validated_data):
        instancia_gestora_data = validated_data.pop('instancia_gestora', [])
        procedencia_fondos_data = validated_data.pop('procedencia_fondos', [])
        # Crear proyecto sin el campo M2M
        proyecto = Proyecto.objects.create(**validated_data)
        # Asignar M2M después
        if instancia_gestora_data:
            proyecto.instancia_gestora.set(instancia_gestora_data)
        if procedencia_fondos_data:
            proyecto.procedencia_fondos.set(procedencia_fondos_data)    

        # Crear nodo para DiagramaEstructura con info actualizada
        nodo = {
            "id": "1",
            "type": "proyecto",
            "dimensions": {
                "width": 500,
                "height": 445
            },
            "computedPosition": {"x": 0, "y": 0, "z": 0},
            "handleBounds": {
                "source": [{
                    "id": "source-1",
                    "type": "source",
                    "nodeId": "1",
                    "position": "bottom",
                    "x": 244,
                    "y": 439.0625,
                    "width": 12,
                    "height": 12
                }],
                "target": None
            },
            "selected": False,
            "dragging": False,
            "resizing": False,
            "initialized": False,
            "isParent": False,
            "position": {"x": 0, "y": 0},
            "data": {
                "label": "Proyecto",
                "type": "proyecto",
                "estado": proyecto.estado,
                "datosNodo": {
                    "id": proyecto.id,
                    "codigo": proyecto.codigo,
                    "titulo": proyecto.titulo,
                    "descripcion": proyecto.descripcion,
                    "fecha_creacion": proyecto.fecha_creacion.isoformat() if proyecto.fecha_creacion else None,
                    "fecha_inicio": proyecto.fecha_inicio.isoformat() if proyecto.fecha_inicio else None,
                    "fecha_finalizacion": proyecto.fecha_finalizacion.isoformat() if proyecto.fecha_finalizacion else None,
                    "presupuesto": str(proyecto.presupuesto),
                    "estado": proyecto.estado,
                    "creado_por": str(proyecto.creado_por),
                    "pei": proyecto.pei_id,
                    "instancia_gestora": list(proyecto.instancia_gestora.values_list('id', flat=True)),
                    "procedencia_fondos": list(proyecto.procedencia_fondos.values_list('id', flat=True))
                }
            },
            "events": {}
        }

        DiagramaEstructura.objects.create(
            proyecto=proyecto,
            codigoProyecto=proyecto.codigo,
            nodos=[nodo],
            conexiones=[]
        )

        return proyecto
        

#Serializador de un proyecto
class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = '__all__'


#Serializador MOdel Objetivo General
class ProyObjGralSer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoGeneralProyecto
        fields = '__all__'        

#serializador MOdel Objetivo especifico
class ProyObjEspSer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoEspecificoProyecto
        fields = '__all__'        

#Serializador Model Kpi
class KpiSer(serializers.ModelSerializer):
    class Meta:
        model = Kpi
        fields = '__all__'

#Serializador Model: Instancia Gestora
class ProyInsGestSer(serializers.ModelSerializer):
    class Meta:
        model = InstanciaGestora
        fields = '__all__'     


#Serializador Model: ProcedenciaFondos
class ProcedenciaFondosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedenciaFondos
        fields = '__all__'     

#Serializador Model: DiagramaEstructura
class DiagramaEstructuraSer(serializers.ModelSerializer):
    class Meta:
        model = DiagramaEstructura
        fields = '__all__'

#Serializador Actualizar los nodos y edges
class DiagramaEstructuraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagramaEstructura
        fields = ['nodos', 'conexiones']

##NO MODELOS
#Solo proyectos en estado de Planificacion
class ProyectoPlanificacionSerializer(serializers.ModelSerializer):
    instancia_gestora = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Proyecto
        fields = [
            'id', 'codigo', 'titulo', 'descripcion',
            'fecha_creacion', 'fecha_inicio', 'fecha_finalizacion',
            'presupuesto', 'estado', 'creado_por', 'pei', 'instancia_gestora'
        ]

#Proyecto - estructura -serializador
class InstanciaGestoraSer(serializers.ModelSerializer):
    class Meta:
        model = InstanciaGestora
        fields = ['codigo', 'clasificador', 'instancia']

class ProyectoEstructuraSer(serializers.ModelSerializer):
    mapa_nodo = DiagramaEstructuraSer(read_only=True)
    instancia_gestora = InstanciaGestoraSer(many=True, read_only = True)
    class Meta:
        model = Proyecto
        fields = ['id', 'codigo', 'titulo', 'descripcion', 'estado', 'fecha_creacion',
                  'fecha_inicio', 'fecha_finalizacion', 'presupuesto', 'pei',
                  'instancia_gestora', 'creado_por', 'mapa_nodo']


#Serializador para el Indicador de Objetivo Especifico
class IndicadorObjetivoGralSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoGeneral
        fields = '__all__'

#Serializador para el Resultado de Objetivo General
class ResultadoOGSerializaer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoOG
        fields = '__all__'

#Serializador Resultado Objetivo Especifico
class ResultadoOESer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoOE
        fields = '__all__'

#Serializador Producto Objetivo Especifico
class ProductoOESer(serializers.ModelSerializer):
    class Meta:
        model = ProductoOE
        fields = '__all__'        

#Serializador para el Indicador de Resultado de Objetivo General
class IndicadorResultadoObjGralSerializ(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjGral
        fields = '__all__'        

#Serializador para Indicador de Objetivo Especifico OG
class IndicadorObjetivoEspecificoSer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoEspecifico
        fields = '__all__'

#Serializador Indicador Resultado OE
class IndicadorResultadoOESer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjEspecifico
        fields = '__all__'

#Serializador Producto Resultado OE
class ProductoResultadoOESer(serializers.ModelSerializer):
    class Meta:
        model = ProductoResultadoOE
        fields = '__all__'

#Serializador para el Producto General
class ProductoGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoGeneral
        fields = '__all__'

#Serializador Proceso
class ProcesosSerializador(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = '__all__'      


#Serializador Actividad
class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'

############################################## ESTRUCTURA COMPLETA DEL PROYECTO   #####################################################
# Serializador KPI
class KpiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kpi
        fields = '__all__'

class IndicadorOgSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoGeneral
        fields = '__all__'

class IndicadorResultadoOgSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjGral
        fields = '__all__'

class ActividadSer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'

class ProcesoSerializer(serializers.ModelSerializer):
    actividades = ActividadSer(many=True, source='actividad_proceso.all')
    class Meta:
        model = Proceso
        fields = '__all__'    

class ResultadoOgSerializer(serializers.ModelSerializer):
    indicador_res_og = IndicadorResultadoOgSerializer(many=True)
    proceso_resultado_og = ProcesoSerializer(many=True)
    actividad_resultado_og = ActividadSer(many=True)    
    class Meta:
        model = ResultadoOG
        fields = '__all__'    

class IndicadorOeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoEspecifico
        fields = '__all__'

class IndicadorResultadoOeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjEspecifico
        fields = '__all__'

class ProductoOeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoOE
        fields = '__all__'    

class ResultadoOeSerializer(serializers.ModelSerializer):
    indicador_res_oe = IndicadorResultadoOeSerializer(many=True)
    productos_res_oe = ProductoOeSerializer(many=True)
    proceso_resultado_oe = ProcesoSerializer(many=True)
    actividad_resultado_oe = ActividadSerializer(many=True)    
    class Meta:
        model = ResultadoOE
        fields = '__all__'

class ProductoOeSerializer(serializers.ModelSerializer):
    proceso_producto_oe = ProcesoSerializer(many=True)
    actividad_producto_oe = ActividadSerializer(many=True)    
    class Meta:
        model = ProductoOE
        fields = '__all__'     

class ObjetivoEspecificoProySerializer(serializers.ModelSerializer):
    indicador_oe = IndicadorOeSerializer(many=True)
    resultados_oe = ResultadoOeSerializer(many=True)
    productos_oe = ProductoOeSerializer(many=True)    
    class Meta:
        model = ObjetivoEspecificoProyecto
        fields = '__all__'         

class ObjetivoGeneralProySerializer(serializers.ModelSerializer):
    kpis = KpiSerializer(many=True)
    indicador_og = IndicadorOgSerializer(many=True)
    resultados_og = ResultadoOgSerializer(many=True)
    objetivos_especificos_og = ObjetivoEspecificoProySerializer(many=True)    
    class Meta:
        model = ObjetivoGeneralProyecto
        fields = '__all__'

# Estructura del proyecto
class ProyectoEstructuraSerializer(serializers.ModelSerializer):
    objetivo_general = ObjetivoGeneralProySerializer()
    objetivos_especificos = ObjetivoEspecificoProySerializer(many=True)
    instancia_gestora = serializers.SlugRelatedField(many=True, read_only=True, slug_field='codigo')
    procedencia_fondos = serializers.SlugRelatedField(many=True, read_only=True, slug_field='sigla')
    class Meta:
        model = Proyecto
        fields = [
            'id', 'codigo', 'titulo', 'descripcion',
            'fecha_creacion', 'fecha_inicio', 'fecha_finalizacion',  
            'estado', 'presupuesto', 
            'instancia_gestora', 'procedencia_fondos', 'objetivo_general', 'objetivos_especificos'
            ]

############################################## FIN ESTRUCTURA COMPLETA DEL PROYECTO   #####################################################



###################################  Lista de procesos de un proyecto  ######################33
class ProcesoProyectoSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Proceso
        fields = ['id', 'codigo', 'titulo', 'display_name']

    def get_display_name(sel, obj):
        return f"{obj.id} - {obj.codigo} - {obj.titulo}"   



################################### Fin Lista de procesos de un proyecto  ######################
