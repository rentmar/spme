#informeactividadprincipal/views/crear_informe_actividad_principal_v2_views.py
import logging
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
######################### SERVICIO #############################
#Servicio - Informe Actividad Principal
from spme_monitoreo.services.informe_actividad_principal_service import InformaActividadPrincipalService
#Servicio - Bitacoras de los indicadores
from spme_proyectos_reportes.services.indicadores import (
    BitacoraOgService,
    BitacoraOeService,
    BitacoraRogService,
    BitacoraRoeService, 
)
#Servicio - Validacion Informe Actividad Principal
from spme_validaciones.services.validacion_informe_actividad_service import ValidacionInformeActividadService
#Servicio -  Vinculacion de sol de viajes a Informe de actividad principal
from spme_monitoreo.services.vinculacion_solicitud_viaje_informe_service import VinculacionSolicitudViajeInformeService
#Servicio de notificaciones
from spme_mensajes.services.notificacion_service import crear_mensajes_validacion_informe
######################### NOTIFICACIONES EMAIL ###########################
#Sistema de encolado de emails
from spme_monitor_estados.utils.encolar import encolar_validacion_pendiente
######################### SERIALIZER ###########################
#Serializer - Informe Actividad Principal 
from ..serializers.crear_informe_actividad_principal_v2_serializer import InformeActividadPrincipalSerializer
######################### Modelos ###########################
from spme_monitoreo.models import Actividad


logger = logging.getLogger(__name__)


class InformeActividadPrincipalV2(APIView):

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

        #Impresion - valor bandera
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
        #Validacion con serializer
        serializer = InformeActividadPrincipalSerializer(data=informe_data)
        serializer.is_valid(raise_exception=True)

        # ============================================================
        # TRANSACCIÓN
        # ============================================================

        try:
            with transaction.atomic():
                #1. Crear el informe de actividad principal y cargar la actividad a la que pertenece
                informe_creado = InformaActividadPrincipalService.crear(serializer.validated_data)
                logger.info(f"✅ Informe creado: {informe_creado.numeroInforme}")

                #2. Procesar avanceIndicadores - Bitacoras
                avance = informe_data.get('avanceIndicadores', {})
                bitacoras_indicador_og = 0
                bitacoras_indicador_oe = 0
                bitacoras_indicador_rog = 0
                bitacoras_indicador_roe = 0 

                # Indicador OG
                for item in avance.get('indicadorog', []):
                    BitacoraOgService.crear_actividad(informe_creado, item)
                    bitacoras_indicador_og += 1
                
                # Indicador OE
                for item in avance.get('indicadoroe', []):
                    BitacoraOeService.crear_actividad(informe_creado, item)
                    bitacoras_indicador_oe += 1

                # Indicador ROG
                for item in avance.get('indicadorrog', []):
                    BitacoraRogService.crear_actividad(informe_creado, item)
                    bitacoras_indicador_rog += 1

                # Indicador ROE
                for item in avance.get('indicadorroe', []):
                    BitacoraRoeService.crear_actividad(informe_creado, item)
                    bitacoras_indicador_roe += 1
                
                #3. Procesar validadores
                validadores_creados = ValidacionInformeActividadService.crear_lote_desde_json(
                    informe_creado, validadores
                )
                logger.info(f"✅ Validadores creados: {len(validadores_creados)}")

                #4. Enviar mensajes para validadores
                mensajes_creados, mensajes_errores, mensajes_detalle = crear_mensajes_validacion_informe(
                    informe_creado=informe_creado,  # ← Tu objeto real
                    validadores=validadores          # ← Tus datos del JSON
                )
                logger.info(
                    f"✅ Mensajes creados: {mensajes_creados} | "
                    f"Errores: {mensajes_errores}"
                )

                #4. Enviar emails a validadores
                emails_encolados = 0
                site_url = request.build_absolute_uri('/').rstrip('/')

                for validacion in validadores_creados:
                    validador = validacion.usuarioValidador
                    email = encolar_validacion_pendiente(
                        informe=informe_creado,
                        tipo='actividad',
                        validador=validador,
                        enlace_ver_detalle=f"{site_url}/validar/actividad/{informe_creado.id}",
                        site_url=site_url
                    )                    
                    emails_encolados += 1 

                logger.info(f"📧 Emails encolados: {emails_encolados}")
                
                #5. Procesar vinculacionSolViajes (solo si hay datos)
                vinculaciones_creadas = 0
                if tiene_vinculacion_sol_viajes:
                    creadas = VinculacionSolicitudViajeInformeService.crear_lote_desde_json(
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
                        "mensaje": "Informe creado correctamente",
                        "informe": {
                            "id": informe_creado.id,
                            "numeroInforme": informe_creado.numeroInforme,
                            "bitacoras_indicador_og": bitacoras_indicador_og,
                            "bitacoras_indicador_oe": bitacoras_indicador_oe,
                            "bitacoras_indicador_rog": bitacoras_indicador_rog,
                            "bitacoras_indicador_roe": bitacoras_indicador_roe, 
                            "validadores_creados": len(validadores_creados),
                            "vinculaciones_creadas": vinculaciones_creadas,
                            "mensajes_enviados": mensajes_creados,
                            "mensajes_errores": mensajes_errores,
                            "emails_encolados": emails_encolados,
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            logger.error(f"❌ Error al crear informe: {str(e)}")
            return Response(
                {"mensaje": f"Error al crear informe: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    
    #GET
    def get(self, request):
        return Response(
            {"mensaje": "GET recibido - v2"},
            status=status.HTTP_200_OK
        )
    
    #PUT
    def put(self, request):
        return Response(
            {"mensaje": "PUT recibido - V2"},
            status=status.HTTP_200_OK
        )
