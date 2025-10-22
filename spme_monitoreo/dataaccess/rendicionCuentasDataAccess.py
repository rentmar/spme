from ..models import RendicionCuentas

class RendicionCuentasDataAccess:
    def crearRendicionCuentas(self, rendicionData):
        """
        Crea una nueva rendición de cuentas en la base de datos.
        :param rendicion_data: Datos de la rendición de cuentas.
        :return: Resultado de la creación de la rendición.
        """
        return RendicionCuentas.objects.create(**rendicionData)

    def obtenerRendicionesCuentas(self):
        """
        Obtiene todas las rendiciones de cuentas de la base de datos.
        :return: Lista de rendiciones de cuentas.
        """
        return RendicionCuentas.objects.all()

    def obtenerRendicionDeCuentas(self, filtros):
        """
        Obtiene rendiciones de cuentas - soporta ambos modos:
        - Por ID específico
        - Con filtros (actividad, tarea, usuario)
        - Todas las rendiciones (sin filtros)
        """
        id_rendicion = filtros.get('id_rendicionCuentas')
        
        # MODO 1: Buscar por ID específico (tiene prioridad)
        if id_rendicion:
            try:
                # Buscar la rendición específica por ID
                rendicion = RendicionCuentas.objects.get(id=id_rendicion)
                return [rendicion]  # Devolver como lista para consistencia
            except RendicionCuentas.DoesNotExist:
                return []
        
        # MODO 2: Aplicar filtros o obtener todas
        queryset = RendicionCuentas.objects.all()
        
        # Aplicar filtros si están presentes
        if filtros.get('id_actividad'):
            queryset = queryset.filter(actividad_id=filtros['id_actividad'])
        
        if filtros.get('id_tarea'):
            queryset = queryset.filter(tarea_id=filtros['id_tarea'])
        
        if filtros.get('usuario'):
            queryset = queryset.filter(usuario_id=filtros['usuario'])
        
        return list(queryset)

    def actualizarValidacionRendicionCuentas(self, rendicionData):
        """
        Actualiza las validaciones de una rendición de cuentas existente.

        :param rendicion_data: Datos con las validaciones a actualizar.
        :return: Rendición de cuentas actualizada.
        """
        rendicion_id = rendicionData.get('rendicion_id')
        
        try:
            rendicion = RendicionCuentas.objects.get(id=rendicion_id)
            campos_actualizados = False

            # Verificar cada campo de validación
            if rendicionData.get('validacion_responsable') is not None:
                rendicion.validacionResponsable = rendicionData['validacion_responsable']
                campos_actualizados = True

            if rendicionData.get('validacion_coordinador') is not None:
                rendicion.validacionCoordinador = rendicionData['validacion_coordinador']
                campos_actualizados = True

            if rendicionData.get('validacion_contador') is not None:
                rendicion.validacionContador = rendicionData['validacion_contador']
                campos_actualizados = True

            if rendicionData.get('validacion_administrador') is not None:
                rendicion.validacionAdministrador = rendicionData['validacion_administrador']
                campos_actualizados = True

            if campos_actualizados:
                rendicion.save()
                return {
                    "id": rendicion.id,
                    "mensaje": "Validaciones actualizadas exitosamente",
                    "validacion_responsable": rendicion.validacionResponsable,
                    "validacion_coordinador": rendicion.validacionCoordinador,
                    "validacion_contador": rendicion.validacionContador,
                    "validacion_administrador": rendicion.validacionAdministrador
                }
            else:
                return {
                    "mensaje": "No se proporcionaron campos de validación para actualizar"
                }
                
        except RendicionCuentas.DoesNotExist:
            return {
                "mensaje": f"La rendición de cuentas con ID {rendicion_id} no existe"
            }
        except Exception as e:
            return {
                "mensaje": f"Error al actualizar las validaciones: {str(e)}"
            }
