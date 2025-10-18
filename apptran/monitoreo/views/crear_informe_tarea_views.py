# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from spme_proyectos_reportes.models import (
    BitacoraIndicadorOG, 
    BitacoraIndicadorOE, 
    BitacoraIndicadorROG, 
    BitacoraIndicadorROE
    )
from spme_monitoreo.models import InfTarea
from spme_estructuracion_proyecto.models import (
    IndicadorObjetivoGeneral, 
    IndicadorObjetivoEspecifico, 
    IndicadorResultadoObjGral, 
    IndicadorResultadoObjEspecifico
    )
from ..serializers.crear_informe_tarea_serializer import InfTareaCreateSerializer


def generar_numero_informe(tarea):
    """Genera número de informe automático"""
    try:
        ultimo_informe = InfTarea.objects.filter(tarea=tarea).aggregate(
            Max('numeroInforme')
        )['numeroInforme__max']
        
        if ultimo_informe:
            try:
                numero = int(ultimo_informe.split('-')[-1]) + 1
                return f"INF-{tarea.codigo}-{numero:03d}"
            except (ValueError, IndexError):
                return f"INF-{tarea.codigo}-001"
        else:
            return f"INF-{tarea.codigo}-001"
    except Exception as e:
        raise Exception(f"Error generando número de informe: {str(e)}")

def obtener_indicador(tipo_indicador, indicador_id):
    """Obtiene el indicador específico"""
    modelo_indicador_map = {
        'indicadorog': IndicadorObjetivoGeneral,
        'indicadoroe': IndicadorObjetivoEspecifico,
        'indicadorrog': IndicadorResultadoObjGral,
        'indicadorroe': IndicadorResultadoObjEspecifico,
    }
    
    if tipo_indicador not in modelo_indicador_map:
        raise ValueError(f"Tipo de indicador no válido: {tipo_indicador}")
    
    try:
        return modelo_indicador_map[tipo_indicador].objects.get(id=indicador_id)
    except ObjectDoesNotExist:
        raise ValueError(f"Indicador {tipo_indicador} con id {indicador_id} no existe")

def datos_registrados_validos(datos_registrados):
    """Valida si los datos registrados contienen información para crear bitácora"""
    # Verificar si datosRegistrados está vacío o no tiene valor
    if not datos_registrados:
        return False
    
    # Verificar si tiene el campo 'valor' y no está vacío
    valor = datos_registrados.get('valor')
    if valor is None or valor == '':
        return False
    
    # Verificar si tiene fecha_registro
    if not datos_registrados.get('fecha_registro'):
        return False
    
    return True

def crear_bitacora_individual(tipo_indicador, datos_avance, informe_tarea):
    """Crea una bitácora individual"""
    modelo_bitacora_map = {
        'indicadorog': BitacoraIndicadorOG,
        'indicadoroe': BitacoraIndicadorOE,
        'indicadorrog': BitacoraIndicadorROG,
        'indicadorroe': BitacoraIndicadorROE,
    }
    
    modelo_bitacora = modelo_bitacora_map[tipo_indicador]
    indicador = obtener_indicador(tipo_indicador, datos_avance['nodoproyecto']['id'])
    
    # Preparar datos para la bitácora
    datos_registrados = datos_avance['datosRegistrados']
    
    # ✅ CORRECCIÓN: Validar que los datos registrados sean válidos
    if not datos_registrados_validos(datos_registrados):
        return None  # No crear bitácora si los datos no son válidos
    
    bitacora_data = {
        'tipo_indicador': tipo_indicador,
        'tipo_dato': datos_avance['tipo_dato'],
        'id_indicador': datos_avance['nodoproyecto']['id'],
        'fecha_registro': datos_registrados['fecha_registro'],
        'observaciones': datos_registrados.get('observaciones', ''),
        'archivos_adjuntos': datos_registrados.get('archivos', []),
        'timestamp_registro': datos_registrados.get('timestamp'),
        'snapshot_indicador': datos_avance['nodoproyecto'],
        'informe_tarea': informe_tarea
    }
    
    # Asignar valor según el tipo de dato
    tipo_dato = datos_avance['tipo_dato']
    valor = datos_registrados['valor']
    
    if tipo_dato == 'A-Z':
        bitacora_data['valor_literal'] = valor
    elif tipo_dato == '1-9':
        try:
            bitacora_data['valor_numerico'] = float(valor)
        except (ValueError, TypeError):
            raise ValueError(f"Valor numérico inválido: {valor}")
    elif tipo_dato == '%':
        try:
            porcentaje = float(valor)
            if not (0 <= porcentaje <= 100):
                raise ValueError("El porcentaje debe estar entre 0 y 100")
            bitacora_data['valor_porcentual'] = porcentaje
        except (ValueError, TypeError):
            raise ValueError(f"Valor porcentual inválido: {valor}")
    
    # Crear la bitácora específica
    campo_indicador_map = {
        'indicadorog': 'indicador_og',
        'indicadoroe': 'indicador_oe', 
        'indicadorrog': 'indicador_rog',
        'indicadorroe': 'indicador_roe'
    }
    
    campo_indicador = campo_indicador_map[tipo_indicador]
    bitacora_data[campo_indicador] = indicador
    
    return modelo_bitacora.objects.create(**bitacora_data)

@api_view(['POST'])
@transaction.atomic
def crear_informe_tarea_completo(request):
    """
    Endpoint para crear informe de tarea con bitácoras en una transacción atómica
    """
    try:
        # Validar datos de entrada
        serializer = InfTareaCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos de entrada inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        datos_validados = serializer.validated_data.copy()
        
        # ✅ CORRECCIÓN: Extraer datos para bitácoras antes de guardar
        # 'avance_indicadores' ahora contiene el JSON del formulario
        datos_bitacoras_json = datos_validados.get('avance_indicadores', [])
        
        # Generar número de informe
        tarea = datos_validados['tarea']
        numero_informe = generar_numero_informe(tarea)
        datos_validados['numeroInforme'] = numero_informe
        
        # ✅ GUARDADO DIRECTO COMO JSON: Crear el informe de tarea
        # 'avance_indicadores' se guarda automáticamente como JSON
        informe_tarea = InfTarea.objects.create(**datos_validados)
        
        # Procesar bitácoras individuales (dentro de la misma transacción)
        bitacoras_creadas = []
        bitacoras_omitidas = []  # ✅ Nuevo: para trackear bitácoras omitidas
        
        if datos_bitacoras_json:  # Solo si hay datos para bitácoras
            for index, avance in enumerate(datos_bitacoras_json):
                try:
                    # ✅ CORRECCIÓN: Verificar si datosRegistrados está vacío
                    datos_registrados = avance.get('datosRegistrados', {})
                    
                    if not datos_registrados_validos(datos_registrados):
                        bitacoras_omitidas.append({
                            'indicador_id': avance['nodoproyecto']['id'],
                            'tipo': avance['type'],
                            'razon': 'datosRegistrados vacíos o sin valor'
                        })
                        continue  # ✅ Omitir esta bitácora
                    
                    bitacora = crear_bitacora_individual(
                        avance['type'],
                        avance, 
                        informe_tarea
                    )
                    
                    if bitacora:  # Solo si se creó la bitácora
                        bitacoras_creadas.append({
                            'id': bitacora.id,
                            'tipo': avance['type'],
                            'indicador_id': avance['nodoproyecto']['id'],
                            'tipo_dato': avance['tipo_dato']
                        })
                    
                except Exception as e:
                    # Si falla alguna bitácora, la transacción completa hará rollback
                    raise ValueError(
                        f"Error en bitácora {index + 1} (tipo: {avance['type']}): {str(e)}"
                    )
        
        # Si llegamos aquí, todo fue exitoso - la transacción se commit automáticamente
        response_data = {
            'mensaje': 'Informe y bitácoras creados exitosamente',
            'informe': {
                'id': informe_tarea.id,
                'numero_informe': informe_tarea.numeroInforme,
                'fecha_ejecucion': informe_tarea.fecha_ejecucion,
                'tarea_id': informe_tarea.tarea.id,
                'tarea_codigo': informe_tarea.tarea.codigo,
                'avance_indicadores': informe_tarea.avance_indicadores  
            },
            'bitacoras_creadas': bitacoras_creadas,
            'bitacoras_omitidas': bitacoras_omitidas,  # ✅ Nuevo: información de omisiones
            'total_bitacoras_creadas': len(bitacoras_creadas),
            'total_bitacoras_omitidas': len(bitacoras_omitidas),
            'transaccion': 'exitosa'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except ValueError as ve:
        # Errores de validación de datos
        return Response({
            'error': 'Error en los datos de bitácoras',
            'detalle': str(ve)
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        # Cualquier otro error - la transacción hará rollback automáticamente
        return Response({
            'error': 'Error interno creando informe',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






# def generar_numero_informe(tarea):
#     """Genera número de informe automático"""
#     try:
#         ultimo_informe = InfTarea.objects.filter(tarea=tarea).aggregate(
#             Max('numeroInforme')
#         )['numeroInforme__max']
        
#         if ultimo_informe:
#             try:
#                 numero = int(ultimo_informe.split('-')[-1]) + 1
#                 return f"INF-{tarea.codigo}-{numero:03d}"
#             except (ValueError, IndexError):
#                 return f"INF-{tarea.codigo}-001"
#         else:
#             return f"INF-{tarea.codigo}-001"
#     except Exception as e:
#         raise Exception(f"Error generando número de informe: {str(e)}")

# def obtener_indicador(tipo_indicador, indicador_id):
#     """Obtiene el indicador específico"""
#     modelo_indicador_map = {
#         'indicadorog': IndicadorObjetivoGeneral,
#         'indicadoroe': IndicadorObjetivoEspecifico,
#         'indicadorrog': IndicadorResultadoObjGral,
#         'indicadorroe': IndicadorResultadoObjEspecifico,
#     }
    
#     if tipo_indicador not in modelo_indicador_map:
#         raise ValueError(f"Tipo de indicador no válido: {tipo_indicador}")
    
#     try:
#         return modelo_indicador_map[tipo_indicador].objects.get(id=indicador_id)
#     except ObjectDoesNotExist:
#         raise ValueError(f"Indicador {tipo_indicador} con id {indicador_id} no existe")

# def crear_bitacora_individual(tipo_indicador, datos_avance, informe_tarea):
#     """Crea una bitácora individual"""
#     modelo_bitacora_map = {
#         'indicadorog': BitacoraIndicadorOG,
#         'indicadoroe': BitacoraIndicadorOE,
#         'indicadorrog': BitacoraIndicadorROG,
#         'indicadorroe': BitacoraIndicadorROE,
#     }
    
#     modelo_bitacora = modelo_bitacora_map[tipo_indicador]
#     indicador = obtener_indicador(tipo_indicador, datos_avance['nodoproyecto']['id'])
    
#     # Preparar datos para la bitácora
#     datos_registrados = datos_avance['datosRegistrados']
    
#     bitacora_data = {
#         'tipo_indicador': tipo_indicador,
#         'tipo_dato': datos_avance['tipo_dato'],
#         'id_indicador': datos_avance['nodoproyecto']['id'],
#         'fecha_registro': datos_registrados['fecha_registro'],
#         'observaciones': datos_registrados.get('observaciones', ''),
#         'archivos_adjuntos': datos_registrados.get('archivos', []),
#         'timestamp_registro': datos_registrados.get('timestamp'),
#         'snapshot_indicador': datos_avance['nodoproyecto'],
#         'informe_tarea': informe_tarea
#     }
    
#     # Asignar valor según el tipo de dato
#     tipo_dato = datos_avance['tipo_dato']
#     valor = datos_registrados['valor']
    
#     if tipo_dato == 'A-Z':
#         bitacora_data['valor_literal'] = valor
#     elif tipo_dato == '1-9':
#         try:
#             bitacora_data['valor_numerico'] = float(valor)
#         except (ValueError, TypeError):
#             raise ValueError(f"Valor numérico inválido: {valor}")
#     elif tipo_dato == '%':
#         try:
#             porcentaje = float(valor)
#             if not (0 <= porcentaje <= 100):
#                 raise ValueError("El porcentaje debe estar entre 0 y 100")
#             bitacora_data['valor_porcentual'] = porcentaje
#         except (ValueError, TypeError):
#             raise ValueError(f"Valor porcentual inválido: {valor}")
    
#     # Crear la bitácora específica
#     campo_indicador_map = {
#         'indicadorog': 'indicador_og',
#         'indicadoroe': 'indicador_oe', 
#         'indicadorrog': 'indicador_rog',
#         'indicadorroe': 'indicador_roe'
#     }
    
#     campo_indicador = campo_indicador_map[tipo_indicador]
#     bitacora_data[campo_indicador] = indicador
    
#     return modelo_bitacora.objects.create(**bitacora_data)

# @api_view(['POST'])
# @transaction.atomic
# def crear_informe_tarea_completo(request):
#     """
#     Endpoint para crear informe de tarea con bitácoras en una transacción atómica
#     """
#     try:
#         # Validar datos de entrada
#         serializer = InfTareaCreateSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response({
#                 'error': 'Datos de entrada inválidos',
#                 'detalles': serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         datos_validados = serializer.validated_data.copy()
        
#         # ✅ CORRECCIÓN: Extraer datos para bitácoras antes de guardar
#         # 'avance_indicadores' ahora contiene el JSON del formulario
#         datos_bitacoras_json = datos_validados.get('avance_indicadores', [])
        
#         # Generar número de informe
#         tarea = datos_validados['tarea']
#         numero_informe = generar_numero_informe(tarea)
#         datos_validados['numeroInforme'] = numero_informe
        
#         # ✅ GUARDADO DIRECTO COMO JSON: Crear el informe de tarea
#         # 'avance_indicadores' se guarda automáticamente como JSON
#         informe_tarea = InfTarea.objects.create(**datos_validados)
        
#         # Procesar bitácoras individuales (dentro de la misma transacción)
#         bitacoras_creadas = []
#         if datos_bitacoras_json:  # Solo si hay datos para bitácoras
#             for index, avance in enumerate(datos_bitacoras_json):
#                 try:
#                     bitacora = crear_bitacora_individual(
#                         avance['type'],
#                         avance, 
#                         informe_tarea
#                     )
#                     bitacoras_creadas.append({
#                         'id': bitacora.id,
#                         'tipo': avance['type'],
#                         'indicador_id': avance['nodoproyecto']['id'],
#                         'tipo_dato': avance['tipo_dato']
#                     })
                    
#                 except Exception as e:
#                     # Si falla alguna bitácora, la transacción completa hará rollback
#                     raise ValueError(
#                         f"Error en bitácora {index + 1} (tipo: {avance['type']}): {str(e)}"
#                     )
        
#         # Si llegamos aquí, todo fue exitoso - la transacción se commit automáticamente
#         response_data = {
#             'mensaje': 'Informe y bitácoras creados exitosamente',
#             'informe': {
#                 'id': informe_tarea.id,
#                 'numero_informe': informe_tarea.numeroInforme,
#                 'fecha_ejecucion': informe_tarea.fecha_ejecucion,
#                 'tarea_id': informe_tarea.tarea.id,
#                 'tarea_codigo': informe_tarea.tarea.codigo,
#                 'avance_indicadores': informe_tarea.avance_indicadores  
#             },
#             'bitacoras_creadas': bitacoras_creadas,
#             'total_bitacoras': len(bitacoras_creadas),
#             'transaccion': 'exitosa'
#         }
        
#         return Response(response_data, status=status.HTTP_201_CREATED)
        
#     except ValueError as ve:
#         # Errores de validación de datos
#         return Response({
#             'error': 'Error en los datos de bitácoras',
#             'detalle': str(ve)
#         }, status=status.HTTP_400_BAD_REQUEST)
        
#     except Exception as e:
#         # Cualquier otro error - la transacción hará rollback automáticamente
#         return Response({
#             'error': 'Error interno creando informe',
#             'detalle': str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)