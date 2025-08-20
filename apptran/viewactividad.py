from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from spme_actividades.models import Actividad
from .serializeractividad import ActividadSerializer
from rest_framework.views import APIView
from rest_framework import status
import json
from datetime import datetime


class ActividadViewset(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer

    def list_by_proyecto(self, request, proyecto_id=None):
        actividades = Actividad.objects.filter(
            proyecto_id = proyecto_id
        ).select_related(
            'responsable', 'proyecto'
        )
        serializer = self.get_serializer(actividades, many=True)
        return Response(serializer.data)
    

class PlanActividadesView(APIView):
    def post(self, request,id_proyecto, *args, **kwargs):
               
        #Datos recibidos via peticion
        datos_recibidos = request.data
        
        #Id de proyecto recibida
        idProyecto = id_proyecto

        #Comprobacion de datos json
        if isinstance(datos_recibidos,str):
            matrizActividad = json.loads(datos_recibidos)
            print("No es json")
        else:
            matrizActividad = datos_recibidos    
            print("Es json")

        #Matrices de resultados y separacion
        nuevas_actividades = []
        actividades_actualizar = []
        id_actualizar = []

        #Separando las actividades nuevas y las existentes
        for item in matrizActividad:
            if item['id'] == 0:
                #Creando un modelo
                actividad = Actividad(
                    codigo = item['codigo'],
                    nombreCorto = item['nombreCorto']
                )
                fecha = convertir_fecha_str_a_fecha(item['fecha_inicio'])
                print(fecha)
            else:
                print(item['fecha_inicio'])
                fecha = convertir_fecha_str_a_fecha(item['fecha_inicio'])

                print('\n')

        #Mensaje de respuesta
        mensaje_respuesta = {
            "mensaje": "Actividades recibidas con éxito.",
            "Id del proyecto": idProyecto, 
            "datos_enviados": datos_recibidos
        }
        return Response(mensaje_respuesta, status=status.HTTP_200_OK)
    

#Conversion de strinf a fecha
def convertir_fecha_str_a_fecha(fecha_str):
    """
    Convierte una cadena de texto a un objeto datetime.date,
    manejando varios formatos comunes de fecha.
    
    Args:
        fecha_str (str): La cadena de texto de la fecha.
        
    Returns:
        datetime.date o None: El objeto de fecha si la conversión es exitosa,
                              de lo contrario, None.
    """
    if not fecha_str:
        return None

    # Lista de formatos de fecha comunes
    formatos = [
        "%d/%m/%Y",  # Formato "04/08/2025"
        "%Y-%m-%d",  # Formato "2025-08-04"
        "%m/%d/%Y",  # Formato "08/04/2025"
        "%d-%m-%Y"   # Formato "04-08-2025"
    ]

    for fmt in formatos:
        try:
            # Intenta parsear la fecha con el formato actual
            return datetime.strptime(fecha_str, fmt).date()
        except (ValueError, TypeError):
            # Si el formato no coincide, continúa con el siguiente
            continue

    # Si ninguno de los formatos funcionó, devuelve None
    return None