from ..models import SolicitudReembolso

class SolicitudReembolsoDataAccess:

    def generar_numero_formulario(self):
        """
        Genera automáticamente el número de formulario para reembolso.
        Formato: REPO-001, REPO-002, etc.
        """
        # Obtener el último número de formulario
        ultimo_reembolso = SolicitudReembolso.objects.filter(
            numeroFormulario__startswith='REPO-'
        ).order_by('-numeroFormulario').first()
        
        if ultimo_reembolso and ultimo_reembolso.numeroFormulario:
            try:
                # Extraer el número y incrementarlo
                ultimo_numero = int(ultimo_reembolso.numeroFormulario.split('-')[1])
                nuevo_numero = ultimo_numero + 1
            except (IndexError, ValueError):
                # Si hay error en el formato, empezar desde 1
                nuevo_numero = 1
        else:
            # Si no hay registros, empezar desde 1
            nuevo_numero = 1
        
        # Formatear el número con ceros a la izquierda
        return f"REPO-{nuevo_numero:03d}"
    
    def crearSolicitudReembolso(self, solicitudData):
        """
        Crea una nueva solicitud de reembolso en la base de datos.
        
        :param solicitud_data: Datos de la solicitud de reembolso.
        :return: Resultado de la creación de la solicitud.
        """
        # Generar número de formulario automáticamente
        numero_formulario = self.generar_numero_formulario()
        
        # Agregar el número de formulario a los datos
        solicitudData['numeroFormulario'] = numero_formulario
        
        # Crear la solicitud
        solicitud = SolicitudReembolso.objects.create(**solicitudData)
        
        return solicitud

    def obtenerSolicitudReembolso(self, filtros):
        """
        Obtiene solicitudes de reembolso - soporta ambos modos:
        - Por ID específico
        - Con filtros (actividad, tarea, usuario)
        - Todas las solicitudes (sin filtros)
        """
        id_solicitud = filtros.get('id')  # CAMBIADO de id_solicitudReembolso a id

        # MODO 1: Buscar por ID específico (tiene prioridad)
        if id_solicitud:
            try:
                # Buscar la solicitud específica por ID
                solicitud = SolicitudReembolso.objects.get(id=id_solicitud)
                return [solicitud]  # Devolver como lista para consistencia
            except SolicitudReembolso.DoesNotExist:
                return []

        # MODO 2: Aplicar filtros o obtener todas
        queryset = SolicitudReembolso.objects.all()

        # Aplicar filtros si están presentes
        if filtros.get('id_actividad'):
            queryset = queryset.filter(actividad_id=filtros['id_actividad'])
        if filtros.get('id_tarea'):
            queryset = queryset.filter(tarea_id=filtros['id_tarea'])
        if filtros.get('usuario'):
            queryset = queryset.filter(usuario_id=filtros['usuario'])

        return list(queryset)
    
    def actualizarValidacionSolicitudReembolso(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de reembolso existente.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Solicitud de reembolso actualizada.
        """
        solicitud_id = solicitudData.get('solicitud_id')
        
        try:
            solicitud = SolicitudReembolso.objects.get(id=solicitud_id)
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
                
        except SolicitudReembolso.DoesNotExist:
            return {
                "mensaje": f"La solicitud de reembolso con ID {solicitud_id} no existe"
            }
        except Exception as e:
            return {
                "mensaje": f"Error al actualizar las validaciones: {str(e)}"
            }