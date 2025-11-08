from ..models import SolicitudPagoDirecto, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad
import logging

logger = logging.getLogger(__name__)

class SolicitudPagoDirectoDataAccess:

    def generar_numero_formulario(self):
        """
        Genera automáticamente el número de formulario para pago directo.
        Formato: PAGO-001, PAGO-002, etc.
        """
        # Obtener el último número de formulario
        ultimo_pago = SolicitudPagoDirecto.objects.filter(
            numeroFormulario__startswith='PAGO-'
        ).order_by('-numeroFormulario').first()
        
        if ultimo_pago and ultimo_pago.numeroFormulario:
            try:
                # Extraer el número y incrementarlo
                ultimo_numero = int(ultimo_pago.numeroFormulario.split('-')[1])
                nuevo_numero = ultimo_numero + 1
            except (IndexError, ValueError):
                # Si hay error en el formato, empezar desde 1
                nuevo_numero = 1
        else:
            # Si no hay registros, empezar desde 1
            nuevo_numero = 1
        
        # Formatear el número con ceros a la izquierda
        return f"PAGO-{nuevo_numero:03d}"

    def crearSolicitudPagoDirecto(self, solicitudData):
        """
        Crea una nueva solicitud de pago directo en la base de datos.
        """
        try:
            logger.info(f"Datos recibidos en DataAccess: {solicitudData}")
            
            # Generar número de formulario automáticamente
            numero_formulario = self.generar_numero_formulario()
            
            # Verificar y obtener instancias de modelos relacionados
            forma_pago_id = solicitudData.get('formaPago_id')
            if forma_pago_id:
                forma_pago = FormaPago.objects.get(id=forma_pago_id)
            else:
                raise ValueError("formaPago_id es requerido")
            
            # Obtener otras instancias necesarias
            responsable_id = solicitudData.get('responsable_id')
            coordinador_id = solicitudData.get('coordinador_id')
            usuario_id = solicitudData.get('usuario_id')
            actividad_id = solicitudData.get('actividad_id')
            tarea_id = solicitudData.get('tarea_id')
            
            responsable = Usuario.objects.get(id=responsable_id) if responsable_id else None
            coordinador = Usuario.objects.get(id=coordinador_id) if coordinador_id else None
            usuario = Usuario.objects.get(id=usuario_id) if usuario_id else None
            actividad = Actividad.objects.get(id=actividad_id) if actividad_id else None
            tarea = TareaActividad.objects.get(id=tarea_id) if tarea_id else None
            
            # Crear la solicitud con las instancias correctas
            solicitud = SolicitudPagoDirecto.objects.create(
                numeroFormulario=numero_formulario,
                descripcion_actividad=solicitudData.get('descripcion_actividad'),
                fecha_realizacion=solicitudData.get('fecha_realizacion'),
                objetivo_actividad=solicitudData.get('objetivo_actividad'),
                fuente_financiamiento=solicitudData.get('fuente_financiamiento'),
                detalleDestinoFondos=solicitudData.get('detalleDestinoFondos'),
                formaPago=forma_pago,  # Usar la instancia, no el ID
                lugarSolicitud=solicitudData.get('lugarSolicitud'),
                fechaSolicitud=solicitudData.get('fechaSolicitud'),
                montoSolicitado=solicitudData.get('montoSolicitado'),
                validacionResponsable=solicitudData.get('validacionResponsable', False),
                responsable=responsable,  # Usar la instancia
                validacionCoordinador=solicitudData.get('validacionCoordinador', False),
                coordinador=coordinador,  # Usar la instancia
                usuario=usuario,  # Usar la instancia
                actividad=actividad,  # Usar la instancia
                tarea=tarea,  # Usar la instancia (puede ser None)
                bloquearIconos=solicitudData.get('bloquearIconos', True)
            )
            
            logger.info(f"Solicitud creada exitosamente: {solicitud.id}")
            return solicitud
            
        except FormaPago.DoesNotExist:
            raise ValueError(f"FormaPago con ID {forma_pago_id} no existe")
        except Usuario.DoesNotExist as e:
            raise ValueError(f"Usuario no encontrado: {str(e)}")
        except Actividad.DoesNotExist as e:
            raise ValueError(f"Actividad no encontrada: {str(e)}")
        except Exception as e:
            logger.error(f"Error al crear solicitud de pago directo: {str(e)}")
            raise ValueError(f"Error al crear solicitud de pago directo: {str(e)}")

    def obtenerSolicitudesPagoDirecto(self):
        """
        Obtiene todas las solicitudes de pago directo de la base de datos.

        :return: Lista de solicitudes de pago directo.
        """
        return SolicitudPagoDirecto.objects.all()

    def obtenerSolicitudesPagoDirecto(self, filtros):
        """
        Obtiene solicitudes de pago directo - soporta ambos modos:
        - Por ID específico
        - Con filtros (actividad, tarea, usuario)
        - Todas las solicitudes (sin filtros)
        """
        id_solicitud = filtros.get('id_solicitudPagoDirecto')
        
        # MODO 1: Buscar por ID específico (tiene prioridad)
        if id_solicitud:
            try:
                # Buscar la solicitud específica por ID
                solicitud = SolicitudPagoDirecto.objects.get(id=id_solicitud)
                return [solicitud]  # Devolver como lista para consistencia
            except SolicitudPagoDirecto.DoesNotExist:
                return []
        
        # MODO 2: Aplicar filtros o obtener todas
        queryset = SolicitudPagoDirecto.objects.all()
        
        # Aplicar filtros si están presentes
        if filtros.get('id_actividad'):
            queryset = queryset.filter(actividad_id=filtros['id_actividad'])
        
        if filtros.get('id_tarea'):
            queryset = queryset.filter(tarea_id=filtros['id_tarea'])
        
        if filtros.get('usuario'):
            queryset = queryset.filter(usuario_id=filtros['usuario'])
        
        return list(queryset)
    
    def actualizarValidacionSolicitudPagoDirecto(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de pago directo existente.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Solicitud de pago directo actualizada.
        """
        solicitud_id = solicitudData.get('solicitud_id')
        
        try:
            solicitud = SolicitudPagoDirecto.objects.get(id=solicitud_id)
            campos_actualizados = False

            # Verificar cada campo de validación
            if solicitudData.get('validacion_responsable') is not None:
                solicitud.validacionResponsable = solicitudData['validacion_responsable']
                campos_actualizados = True
                
            if solicitudData.get('validacion_coordinador') is not None:
                solicitud.validacionCoordinador = solicitudData['validacion_coordinador']
                campos_actualizados = True

            if campos_actualizados:
                solicitud.save()
                return {
                    "id": solicitud.id,
                    "mensaje": "Validaciones actualizadas exitosamente",
                    "validacion_responsable": solicitud.validacionResponsable,
                    "validacion_coordinador": solicitud.validacionCoordinador
                }
            else:
                return {
                    "mensaje": "No se proporcionaron campos de validación para actualizar"
                }
                
        except SolicitudPagoDirecto.DoesNotExist:
            return {
                "mensaje": f"La solicitud de pago directo con ID {solicitud_id} no existe"
            }
        except Exception as e:
            return {
                "mensaje": f"Error al actualizar las validaciones: {str(e)}"
            }