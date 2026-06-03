import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
######################### SERVICIO #############################
#Servicio - Bitacoras de los indicadores
from spme_proyectos_reportes.services.indicadores import (
    BitacoraOgService,
    BitacoraOeService,
    BitacoraRogService,
    BitacoraRoeService,
)
#Servicio - validacion de informe de tarea
from spme_validaciones.services.validacion_informe_tarea_service import ValidacionInformeTareaService
#Servicio - vinculacion de sol de viajes
from spme_monitoreo.services.vinculacion_solicitud_viaje_informe_tarea_service import VinculacionSolicitudViajeInformeTareaService
#Servicio - Mensajes
from spme_mensajes.services.notificacion_service import crear_mensajes_validacion_informe_tarea
#Servicio - Emails
from spme_monitor_estados.utils.encolar import encolar_validacion_pendiente
######################### SERIALIZER ###########################
#Serializer del informe de tarea(subactividad)
from ..serializers.crear_informe_tarea_principal_v2_serializer import InformeTareaPrincipalSerializer



logger = logging.getLogger(__name__)

class InformeSubactividadPrincipalV2(APIView):
    #POST
    def post(self, request):

        logger.info(f"JSON recibido: {request.data}")

        #Fragmentar la informacion en tres variables
        informe_data = request.data.get('informeData', {})
        validadores = request.data.get('validadores', [])
        vinculacion_sol_viajes = request.data.get('vinculacionSolViajes')

        #Validar el estado de vinculacionSolViajes
        tiene_vinculacion_sol_viajes = (
            vinculacion_sol_viajes is not None
            and isinstance(vinculacion_sol_viajes, dict)
            and bool(vinculacion_sol_viajes)
        )

        #Impresion - bandera de vinculacion
        if tiene_vinculacion_sol_viajes:
            total = vinculacion_sol_viajes.get('total_solicitudes', 0)
            logger.info(f"✅ Tiene vinculación con {total} solicitudes de viaje")
        else:
            logger.info("⚠️  No tiene vinculación con solicitudes de viaje")
        
        #Impresion de los fragmentos de informacion
        print("=" * 50)
        print("1. INFORME DATA:")
        print(informe_data)
        print("=" * 50)
        print("2. VALIDADORES:")
        print(validadores)
        print("=" * 50)
        print("3. VINCULACION SOL VIAJES:")
        print(vinculacion_sol_viajes)
        print("=" * 50)

        # ============================================================
        # Procesar: informeData
        # ============================================================
        #Validacion con serializer del informe de subactividad
        serializer = InformeTareaPrincipalSerializer(data=informe_data)
        if not serializer.is_valid():
            return Response(
                {"mensaje": "Error de validación", "errores": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ============================================================
        # TRANSACCIÓN
        # ============================================================
        try:
            with transaction.atomic():
                #1.Crear el informe de subactividad
                informe_creado = serializer.save()

                #2. Procesar avanceIndicadores - Indicadores
                avance = informe_data.get('avanceIndicadores', {})
                bitacoras_indicador_og = 0
                bitacoras_indicador_oe = 0
                bitacoras_indicador_rog = 0
                bitacoras_indicador_roe = 0 

                #Solo procesar los indicadores si avance no es None y tiene datos
                if avance and isinstance(avance, dict):
                    #Indicador OG (objetivo general)
                    for item in avance.get('indicadorog', []):
                        BitacoraOgService.crear_tarea(informe_creado, item)  # ← crear_tarea
                        bitacoras_indicador_og += 1
                    
                    # Indicador OE (Objetivo Específico)
                    for item in avance.get('indicadoroe', []):
                        BitacoraOeService.crear_tarea(informe_creado, item)  # ← crear_tarea
                        bitacoras_indicador_oe += 1
                    
                    # Indicador ROG (Resultado Objetivo General)
                    for item in avance.get('indicadorrog', []):
                        BitacoraRogService.crear_tarea(informe_creado, item)  # ← crear_tarea
                        bitacoras_indicador_rog += 1
                    
                    # Indicador ROE (Resultado Objetivo Específico)
                    for item in avance.get('indicadorroe', []):
                        BitacoraRoeService.crear_tarea(informe_creado, item)  # ← crear_tarea
                        bitacoras_indicador_roe += 1
                
                #3. Procesar Validadores
                validaciones_creadas = ValidacionInformeTareaService.crear_lote_desde_json(
                    informe_tarea=informe_creado,
                    validadores_json=validadores
                )
                logger.info(f"✅ {len(validaciones_creadas)} validaciones asignadas")

                #4. Enviar mensajes a validadores
                mensajes_creados, mensajes_errores, mensajes_detalle = crear_mensajes_validacion_informe_tarea(
                    informe_creado=informe_creado,
                    validadores=validadores 
                )
                
                logger.info(
                    f"✅ Mensajes creados: {mensajes_creados} | "
                    f"Errores: {mensajes_errores}"
                )

                #5. Enviar emails a validadores
                emails_encolados = 0
                site_url = request.build_absolute_uri('/').rstrip('/')

                for validacion in validaciones_creadas:
                    validador = validacion.usuarioValidador
                    email = encolar_validacion_pendiente(
                        informe=informe_creado,
                        tipo='tarea',
                        validador=validador,
                        enlace_ver_detalle=f"{site_url}/validar/actividad/{informe_creado.id}",
                        site_url=site_url
                    )                    
                    emails_encolados += 1 

                logger.info(f"📧 Emails encolados: {emails_encolados}")
                

                #6. Procesar vinculaciones - sol de viajes
                vinculaciones_creadas = 0
                if tiene_vinculacion_sol_viajes:
                    creadas = VinculacionSolicitudViajeInformeTareaService.crear_lote_desde_json(
                        informe_creado,
                        vinculacion_sol_viajes,
                        usuario_id=informe_data.get('usuario')
                    )
                    vinculaciones_creadas = len(creadas)
                    logger.info(f"✅ Vinculaciones creadas: {vinculaciones_creadas}")
                else:
                    logger.info("⚠️  Sin vinculaciones para procesar")

                #Respuesta
                return Response(
                    {
                        "mensaje": "Informe subactividad creado correctamente",
                        "informe subactividad":{
                            "id": informe_creado.id,
                            "numeroInforme": informe_creado.numeroInforme,
                            "bitacoras_indicador_og": bitacoras_indicador_og,
                            "bitacoras_indicador_oe": bitacoras_indicador_oe,
                            "bitacoras_indicador_rog": bitacoras_indicador_rog,
                            "bitacoras_indicador_roe": bitacoras_indicador_roe, 
                            "validadores_creados": len(validaciones_creadas),
                            "vinculaciones_creadas": vinculaciones_creadas,
                        },
                    },
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            logger.error(f"❌ Error al crear informe tarea: {str(e)}")
            return Response(
                {"mensaje": f"Error al crear informe tarea: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    




    #GET
    def get(self, request):
        return Response(
            {"mensaje": "GET recibido - TAREA v2"},
            status=status.HTTP_200_OK
        )
    
    def put(self, request):
        return Response(
            {"mensaje": "PUT recibido - TAREA V2"},
            status=status.HTTP_200_OK
        )