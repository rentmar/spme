# spme/spme_presupuesto/services/planificacion_service.py
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad

from spme_presupuesto.repositories.planificacion_repository import PlanificacionRepository


class PlanificacionService:
    """
    Lógica de negocio para consultas de planificación presupuestaria.

    Esta clase utiliza el repositorio para acceder a los datos y aplica
    las transformaciones necesarias para presentar la información.
    """
    
    def __init__(self, repository=None):
        """
        Inicializa el servicio.

        Args:
            repository: Repositorio opcional (testing)        
        """
        self.repository = repository or PlanificacionRepository()
    
    ################### METODOS PUBLICOS ##############################

    def resumen_proyecto(self, proyecto_id):
        """
        Obtiene una vista resumida de la planificacion del proyecto
        
        Incluye:
        - Datos generales del proyecto
        - Fuentes de financiamiento asociadas (M2M)
        - Instancias gestoras asociadas (M2M)
        - Consolidado de presupuesto por fuente
        - Conteo de actividades y tareas

         Args:
            proyecto_id: ID del proyecto
            
        Returns:
            dict con el resumen completo
        """
        proyecto = self.repository.obtener_proyecto(proyecto_id)
        actividades = self.repository.obtener_actividad_planificadas(proyecto_id)

        num_tareas = sum(act.tareas.count() for act in actividades)
        consolidado, total_consolidado = self._consolidar_fuentes(actividades)
        
        mensajes = {
            'ES': 'El proyecto está en estructuración. Aún no se han registrado presupuestos.',
            'EP': 'Proyecto en planificación. Los presupuestos pueden modificarse libremente.',
            'PL': 'Proyecto planificado. La planificación está cerrada. Cambios requieren solicitud formal.',
        }

        return {
            'proyecto_codigo': proyecto.codigo,
            'proyecto_titulo': proyecto.titulo,
            'proyecto_estado': proyecto.estado,
            'presupuesto_global': proyecto.presupuesto or 0,
            'fuentes_asociadas': [
                {'sigla': f.sigla or '', 'financiera': f.financiera or ''}
                for f in proyecto.procedencia_fondos.all()
            ],
            'instancias_gestoras': [
                {'codigo': i.codigo or '', 'instancia': i.instancia}
                for i in proyecto.instancia_gestora.all()
            ],
            'consolidado_por_fuentes': consolidado,
            'total_consolidado': total_consolidado,
            'num_actividades': actividades.count(),
            'num_tareas': num_tareas,
            'mensaje': mensajes.get(proyecto.estado, ''),
        }
    
    def actividades_planificadas(self, proyecto_id, incluir_tareas=False):
        """
        Obtiene la lista de actividades con su presupuesto planificado.
        Args:
            proyecto_id: ID del proyecto
            incluir_tareas: Si es True, incluye el detalle de tareas por actividad
            
        Returns:
            dict con lista de actividades y total planificado
        """
        actividades = self.repository.obtener_actividad_planificadas(proyecto_id)
        resultado = []

        for act in actividades:
            suma_fuentes = self._sumar_fuentes_actividad(act)

            item = {
                'id': act.id,
                'codigo': act.codigo or '',
                'nombre': act.nombreCorto or '',
                'estado': act.estado,
                'tipo': act.tipo.sigla if act.tipo else None,
                'presupuesto': act.presupuesto or 0,
                'procedencia_fondos': act.procedencia_fondos or [],
                'suma_fuentes': suma_fuentes,
                'num_tareas': act.tareas.count(),
                'fecha_programada': act.fecha_programada,
            }

            if incluir_tareas:
                item['tareas'] = self._datos_tareas(act)
            
            resultado.append(item)

        return {
            'actividades': resultado,
            'total_planificado': sum(item['presupuesto'] for item in resultado),
        }
    
    def tareas_planificadas(self, actividad_id):
        """
        Obtiene el detalle de tareas planificadas de una actividad.

        Para cada tarea, extrae la lista de partidas desde presupuestoDesglose
        y calcula la suma de todas las partidas.

        Args:
            actividad_id: ID de la actividad
            
        Returns:
            dict con lista de tareas y total planificado
        """
        actividad = Actividad.objects.get(id=actividad_id)
        tareas = self.repository.obtener_tareas_planificadas(actividad_id)

        tareas_data = []
        for tarea in tareas:
            # presupuestoDesglose es una lista de partidas
            # Formato: [{"partida": "1.1.1", "descripcion": "...", "monto": 100}]
            partidas = []
            suma_partidas = 0
            if tarea.presupuestoDesglose and isinstance(tarea.presupuestoDesglose, list):
                partidas = tarea.presupuestoDesglose
                suma_partidas = sum(float(p.get('monto', 0)) for p in partidas)
            
            tareas_data.append({
                'id': tarea.id or '',
                'codigo': tarea.codigo or '',
                'titulo': tarea.titulo or 'Sin título',
                'presupuesto': tarea.presupuesto or 0,
                'estado': tarea.estado,
                'partidas': partidas,
                'suma_partidas': suma_partidas,
                'fecha_limite': tarea.fecha_limite,
                'actividad_id': tarea.actividad.id,
            })
        
        return {
            'actividad_id': actividad.id or '',
            'actividad_codigo': actividad.codigo or '',
            'actividad_nombre': actividad.nombreCorto or '',
            'tareas': tareas_data,
            'total_planificado': sum(t['presupuesto'] for t in tareas_data),
        }
    
    def consolidado_por_fuente(self, proyecto_id):
        """
        Consolida el presupuesto planificado por cada fuente de financiamiento.
        
        Recorre todas las actividades y acumula los montos desde el campo
        procedencia_fondos (JSON). Incluye fuentes del M2M aunque no tengan
        monto asignado aún.
        
        Args:
            proyecto_id: ID del proyecto
            
        Returns:
            dict con lista de fuentes y total global
        """
        proyecto = self.repository.obtener_proyecto(proyecto_id)
        actividades = self.repository.obtener_actividad_planificadas(proyecto_id)

        #Inicializar diccionario con fuentes M2M
        fuentes_dict = {}
        for fuente in proyecto.procedencia_fondos.all():
            fuentes_dict[fuente.financiera] = {
                'nombre': fuente.financiera,
                'planificado_total': 0,
                'actividades': [],
                'manual': False,
            }
        
        # Recorrer actividades y acumular montos desde JSON
        for act in actividades:
            if act.procedencia_fondos and isinstance(act.procedencia_fondos, list):
                for f in act.procedencia_fondos:
                    nombre = f.get('nombre', 'Desconocido')
                    monto = float(f.get('monto', 0))
                    manual = f.get('manual', False)
                    
                    if nombre not in fuentes_dict:
                        fuentes_dict[nombre] = {
                            'nombre': nombre,
                            'planificado_total': 0,
                            'actividades': [],
                            'manual': manual,
                        }
                    
                    fuentes_dict[nombre]['planificado_total'] += monto
                    fuentes_dict[nombre]['actividades'].append({
                        'actividad': act.codigo or '',
                        'monto': monto,
                    })

        total_global = sum(f['planificado_total'] for f in fuentes_dict.values())

        fuentes = []

        for nombre, datos in fuentes_dict.items():
            datos['porcentaje'] = round(
                (datos['planificado_total'] / total_global * 100), 2
            ) if total_global > 0 else 0
            fuentes.append(datos)
        
        return {
            'fuentes': fuentes,
            'total_global': total_global,
        }





            

        


    ################### METODOS PRIVADOS ##############################

    def _consolidar_fuentes(self, actividades):
        """
        Consolida montos por fuente desde actividades.
        Retorna un diccionario {nombre: monto} y el total.
        """
        consolidado = {}
        total = 0
        for act in actividades:
            if act.procedencia_fondos and isinstance(act.procedencia_fondos, list):
                for f in act.procedencia_fondos:
                    nombre = f.get('nombre', 'Desconocido')
                    monto = float(f.get('monto', 0))
                    consolidado[nombre] = consolidado.get(nombre, 0) + monto
                    total += monto
        
        return {k: round(v, 2) for k, v in consolidado.items()}, round(total, 2)
    
    def _sumar_fuentes_actividad(self, actividad):
        """
        Suma los montos de procedencia_fondos de una actividad
        """
        if not actividad.procedencia_fondos or not isinstance(actividad.procedencia_fondos, list):
            return 0
        return sum(float(f.get('monto', 0)) for f in actividad.procedencia_fondos)
    
    def _datos_tareas(self, actividad):
        """
        Obtiene datos de Tareas de una Actividad
        """
        tareas = actividad.tareas.all()
        datos = []
        for tarea in tareas:
            partidas = []
            suma_partidas = 0
            if tarea.presupuestoDesglose and isinstance(tarea.presupuestoDesglose, list):
                partidas = tarea.presupuestoDesglose
                suma_partidas = sum(float(p.get('monto', 0)) for p in partidas)
            
            datos.append({
                'id': tarea.id,
                'codigo': tarea.codigo or '',
                'titulo': tarea.titulo or 'Sin título',
                'presupuesto': tarea.presupuesto or 0,
                'estado': tarea.estado,
                'partidas': partidas,
                'suma_partidas': suma_partidas,
                'fecha_limite': tarea.fecha_limite,
                'actividad_id': actividad.id,
            })
        
        return datos


    
    