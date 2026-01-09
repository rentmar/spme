from django.db import models
from spme_estructuracion_proyecto.models import Proyecto
from django.db import models
#utils
from django.utils import timezone
#Auditlog
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
#Modelos
from spme_estructuracion_pei.models import (
    Pei
    )
#Modelos usuario
from spme_autenticacion.models import Usuario

 
#Almacena la planificacion completa de un proyecto para seguimiento
class PlanificacionProyecto(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='planificaciones',
        blank=True,
        null=True,
    )
    table_config = models.JSONField(null=True, blank=True)
    rows_data = models.JSONField(null=True, blank=True)
    version = models.IntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    creado_por = models.CharField(max_length=255, null=True, blank=True)
    vigente = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-version']
        unique_together = ['proyecto', 'version']
        verbose_name = 'Planificacion Proyecto'
        verbose_name_plural = 'Planificaciones Proyecto'

    def __str__(self):
        return f'Plan de {self.proyecto} - version {self.version}'    



#Registra cambios especificos en la planificacion
class CambioPlanificacion(models.Model):
    TIPO_CAMBIO = [
        ('creacion', 'Creación'),
        ('actualizacion', 'Actualización'),
        ('eliminacion', 'Eliminación'),
        ('reprogramacion', 'Reprogramación'),
    ]    
    planificacion = models.ForeignKey(
        PlanificacionProyecto,
        on_delete=models.CASCADE,
        related_name='cambios',
        blank=True,
        null=True,
    )
    tipo_cambio = models.CharField(max_length=20, choices=TIPO_CAMBIO)
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    realizado_por = models.CharField(max_length=255, null=True, blank=True)
    realizado_el = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-realizado_el']
        verbose_name = 'Cambio planificacion'
        verbose_name_plural = 'Cambios planificacion'

    def __str__(self):
        return f'Cambio para: { self.planificacion }'    





#Proyecto de planificaciones
class ProyectoPlan(models.Model):
    table_config = models.JSONField(null=True, blank=True)
    rows_data = models.JSONField(null=True, blank=True)
    version = models.IntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    #Relacion
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='planificacion'
    )

#Revision de plan
class PlanRevision(models.Model):
    cambios = models.JSONField(null=True, blank=True)
    razon = models.TextField(null=True, blank=True)
    #modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modificado_por = models.CharField(null=True, blank=True, max_length=100)
    modificado_el = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()
    #Relacion
    plan = models.ForeignKey(
        ProyectoPlan,
        on_delete=models.CASCADE,
        related_name='revisiones'
    )
    class Meta:
        ordering = ['-modificado_el']


########################## SEGUIMIENTO DE LA PLANIFICACION PEI ###########################

class PlanificacionPei(models.Model):
    """
    Modelo principal para planificación PEI.
    Incluye seguimiento completo de quién, cuándo y qué se modificó.
    """
    
    # -----------------------------------------------------------------
    # 1. RELACIONES PRINCIPALES
    # -----------------------------------------------------------------
    pei = models.OneToOneField(
        Pei,  # Asegúrate que 'Pei' esté importado o use string
        on_delete=models.CASCADE,
        related_name='planificacion_pei',
        verbose_name='PEI Relacionado',
        help_text='Cada PEI tiene una única planificación'
    )
    
    # -----------------------------------------------------------------
    # 2. DATOS DEL FRONTEND (VUE COMPONENT)
    # -----------------------------------------------------------------
    datos_tabla = models.JSONField(
        verbose_name='Datos de actividades',
        default=list,
        help_text='Estructura JSON completa de actividades y subactividades'
    )
    
    configuracion = models.JSONField(
        verbose_name='Configuración de tabla',
        default=dict,
        blank=True,
        help_text='Columnas, fórmulas, formatos de visualización'
    )
    
    # -----------------------------------------------------------------
    # 3. CONTROL DE VERSIONES
    # -----------------------------------------------------------------
    version = models.IntegerField(
        default=1,
        verbose_name='Versión',
        help_text='Número de versión, se incrementa automáticamente al guardar cambios'
    )
    
    # -----------------------------------------------------------------
    # 4. SEGUIMIENTO DE USUARIO (QUIÉN)
    # -----------------------------------------------------------------
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planificaciones_creadas',
        verbose_name='Creado por',
        help_text='Usuario que creó esta planificación'
    )
    
    actualizado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planificaciones_modificadas',
        verbose_name='Última modificación por',
        help_text='Usuario que realizó la última modificación'
    )
    
    # -----------------------------------------------------------------
    # 5. CAMPOS CALCULADOS AUTOMÁTICAMENTE
    # -----------------------------------------------------------------
    total_actividades = models.IntegerField(
        default=0,
        verbose_name='Total de actividades',
        help_text='Calculado automáticamente de datos_tabla'
    )
    
    total_subactividades = models.IntegerField(
        default=0,
        verbose_name='Total de subactividades',
        help_text='Calculado automáticamente de datos_tabla'
    )
    
    total_presupuesto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Presupuesto total',
        help_text='Suma de presupuestos de actividades principales'
    )
    
    actividades_planificadas = models.IntegerField(
        default=0,
        verbose_name='Actividades planificadas',
        help_text='Actividades con fechas de inicio y fin definidas'
    )
    
    # -----------------------------------------------------------------
    # 6. TIMESTAMPS AUTOMÁTICOS (CUÁNDO)
    # -----------------------------------------------------------------
    creado_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    actualizado_el = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de última actualización'
    )
    
    # -----------------------------------------------------------------
    # 7. SISTEMA DE AUDITORÍA AUTOMÁTICO (AUDIT LOG)
    # -----------------------------------------------------------------
    history = AuditlogHistoryField(
        verbose_name='Historial de cambios',
        help_text='Registro automático de todos los cambios realizados'
    )
    
    class Meta:
        verbose_name = 'Planificación PEI'
        verbose_name_plural = 'Planificaciones PEI'
        ordering = ['-actualizado_el']
        indexes = [
            # Index para búsquedas comunes
            models.Index(fields=['pei']),
            models.Index(fields=['version']),
            models.Index(fields=['creado_por']),
            models.Index(fields=['actualizado_por']),
            models.Index(fields=['creado_el']),
            models.Index(fields=['actualizado_el']),
            # Index para reportes
            models.Index(fields=['total_actividades']),
            models.Index(fields=['total_presupuesto']),
        ]
    
    def __str__(self):
        return f"Planificación #{self.id} - {self.pei.titulo} (v{self.version})"
    
    # -----------------------------------------------------------------
    # MÉTODOS PRINCIPALES
    # -----------------------------------------------------------------
    
    def save(self, *args, **kwargs):
        """
        Sobreescribir save para:
        1. Incrementar versión en actualizaciones
        2. Calcular estadísticas automáticas
        3. Manejar lógica de usuario
        """
        # Incrementar versión solo si es una actualización (ya existe en BD)
        es_actualizacion = bool(self.pk)
        
        if es_actualizacion:
            self.version += 1
        
        # Calcular estadísticas antes de guardar
        self._calcular_estadisticas()
        
        # Llamar al save original
        super().save(*args, **kwargs)
    
    def _calcular_estadisticas(self):
        """
        Calcular todos los campos automáticos basados en datos_tabla.
        Se ejecuta automáticamente antes de cada save().
        """
        try:
            datos = self.datos_tabla or []
            
            # Reiniciar contadores
            actividades = 0
            subactividades = 0
            presupuesto_total = 0.0
            planificadas = 0
            
            for item in datos:
                # Determinar nivel (0 = actividad, 1 = subactividad)
                nivel = item.get('nivel', 0)
                
                if nivel == 0:  # Actividad principal
                    actividades += 1
                    
                    # Verificar si está planificada
                    if item.get('fecha_inicio_plan') and item.get('fecha_fin_plan'):
                        planificadas += 1
                    
                    # Sumar presupuesto
                    try:
                        presupuesto = float(item.get('presupuesto', 0) or 0)
                        presupuesto_total += presupuesto
                    except (ValueError, TypeError):
                        pass
                    
                    # Contar subactividades dentro de esta actividad
                    if 'subactividades' in item and isinstance(item['subactividades'], list):
                        subactividades += len(item['subactividades'])
                
                elif nivel == 1:  # Subactividad directa
                    subactividades += 1
            
            # Actualizar campos
            self.total_actividades = actividades
            self.total_subactividades = subactividades
            self.total_presupuesto = presupuesto_total
            self.actividades_planificadas = planificadas
            
        except Exception as e:
            # Si hay error en el cálculo, mantener valores actuales
            # y registrar el error (en producción usar logging)
            print(f"⚠️ Error calculando estadísticas para planificación {self.id}: {e}")
            # No lanzar excepción para no interrumpir el save()
    
    # -----------------------------------------------------------------
    # MÉTODOS DE UTILIDAD PARA CONSULTAS
    # -----------------------------------------------------------------
    
    def obtener_resumen_auditoria(self):
        """
        Obtener resumen completo de auditoría para esta planificación.
        
        Returns:
            dict: Información estructurada de creación y modificación
        """
        return {
            'creacion': {
                'usuario': self._obtener_info_usuario(self.creado_por),
                'fecha': self.creado_el,
                'version': 1  # La creación siempre es versión 1
            },
            'ultima_modificacion': {
                'usuario': self._obtener_info_usuario(self.actualizado_por),
                'fecha': self.actualizado_el,
                'version': self.version
            },
            'estadisticas_actuales': {
                'total_actividades': self.total_actividades,
                'total_subactividades': self.total_subactividades,
                'actividades_planificadas': self.actividades_planificadas,
                'actividades_sin_planificar': self.total_actividades - self.actividades_planificadas,
                'porcentaje_planificacion': (
                    (self.actividades_planificadas / self.total_actividades * 100)
                    if self.total_actividades > 0 else 0
                ),
                'presupuesto_total': float(self.total_presupuesto)
            }
        }
    
    def obtener_historial_cambios(self):
        """
        Obtener historial de cambios desde Audit Log.
        
        Returns:
            QuerySet: Todos los logs de cambios para esta planificación
        """
        return self.history.all().order_by('-timestamp')
    
    def obtener_cambios_entre_versiones(self, version_inicial, version_final):
        """
        Obtener cambios específicos entre dos versiones.
        
        Args:
            version_inicial (int): Versión inicial
            version_final (int): Versión final
            
        Returns:
            list: Lista de cambios entre las versiones
        """
        cambios = []
        logs = self.history.filter(
            changes__version__isnull=False
        ).order_by('timestamp')
        
        for log in logs:
            if 'version' in log.changes:
                version_log = log.changes['version'].get('new')
                if version_inicial <= version_log <= version_final:
                    cambios.append({
                        'version': version_log,
                        'timestamp': log.timestamp,
                        'usuario': self._obtener_info_usuario(log.actor),
                        'cambios': log.changes
                    })
        
        return cambios
    
    def _obtener_info_usuario(self, usuario):
        """
        Obtener información estructurada de un usuario.
        
        Args:
            usuario: Instancia del modelo Usuario o None
            
        Returns:
            dict or None: Información del usuario o None
        """
        if not usuario:
            return None
        
        return {
            'id': usuario.id,
            'username': usuario.username,
            'nombre_completo': usuario.get_full_name(),
            'cargo': usuario.cargo if hasattr(usuario, 'cargo') else None,
            'correo': usuario.correo if hasattr(usuario, 'correo') else None
        }
    
    # -----------------------------------------------------------------
    # PROPIEDADES CALCULADAS (PARA TEMPLATES Y APIs)
    # -----------------------------------------------------------------
    
    @property
    def porcentaje_planificacion(self):
        """Porcentaje de actividades planificadas"""
        if self.total_actividades == 0:
            return 0
        return (self.actividades_planificadas / self.total_actividades) * 100
    
    @property
    def actividades_sin_planificar(self):
        """Número de actividades sin planificar"""
        return self.total_actividades - self.actividades_planificadas
    
    @property
    def tiempo_desde_ultima_modificacion(self):
        """Tiempo transcurrido desde la última modificación"""
        return timezone.now() - self.actualizado_el
    
    @property
    def es_reciente(self):
        """¿Fue modificada en las últimas 24 horas?"""
        return self.tiempo_desde_ultima_modificacion.days == 0
    
    # -----------------------------------------------------------------
    # MÉTODOS PARA OPERACIONES ESPECÍFICAS
    # -----------------------------------------------------------------
    
    def crear_nueva_version(self, usuario, datos_tabla=None, configuracion=None):
        """
        Crear una nueva versión manualmente.
        
        Args:
            usuario: Usuario que crea la nueva versión
            datos_tabla (optional): Nuevos datos de tabla
            configuracion (optional): Nueva configuración
            
        Returns:
            PlanificacionPei: La nueva versión creada
        """
        nueva_version = PlanificacionPei.objects.create(
            pei=self.pei,
            datos_tabla=datos_tabla or self.datos_tabla.copy(),
            configuracion=configuracion or self.configuracion.copy(),
            creado_por=self.creado_por,  # Mantener creador original
            actualizado_por=usuario,     # Nuevo actualizador
            version=self.version + 1     # Incrementar versión
        )
        
        return nueva_version
    
    def obtener_actividades_por_responsable(self):
        """
        Agrupar actividades por responsable.
        
        Returns:
            dict: Actividades agrupadas por responsable
        """
        actividades_por_responsable = {}
        datos = self.datos_tabla or []
        
        for item in datos:
            if item.get('nivel', 0) == 0:  # Solo actividades principales
                responsable = item.get('responsable', 'Sin asignar')
                
                if responsable not in actividades_por_responsable:
                    actividades_por_responsable[responsable] = {
                        'total': 0,
                        'planificadas': 0,
                        'presupuesto_total': 0.0,
                        'actividades': []
                    }
                
                actividades_por_responsable[responsable]['total'] += 1
                
                # Verificar si está planificada
                if item.get('fecha_inicio_plan') and item.get('fecha_fin_plan'):
                    actividades_por_responsable[responsable]['planificadas'] += 1
                
                # Sumar presupuesto
                try:
                    presupuesto = float(item.get('presupuesto', 0) or 0)
                    actividades_por_responsable[responsable]['presupuesto_total'] += presupuesto
                except (ValueError, TypeError):
                    pass
                
                # Agregar actividad a la lista
                actividades_por_responsable[responsable]['actividades'].append({
                    'id': item.get('id'),
                    'nombre': item.get('actividad', 'Sin nombre'),
                    'planificada': bool(item.get('fecha_inicio_plan') and item.get('fecha_fin_plan')),
                    'presupuesto': item.get('presupuesto', 0)
                })
        
        return actividades_por_responsable
    
    def to_dict(self):
        """
        Convertir modelo a diccionario para serialización.
        
        Returns:
            dict: Representación completa del modelo
        """
        return {
            'id': self.id,
            'pei_id': self.pei.id,
            'pei_titulo': self.pei.titulo,
            'datos_tabla': self.datos_tabla,
            'configuracion': self.configuracion,
            'version': self.version,
            'creado_por': self._obtener_info_usuario(self.creado_por),
            'actualizado_por': self._obtener_info_usuario(self.actualizado_por),
            'estadisticas': {
                'total_actividades': self.total_actividades,
                'total_subactividades': self.total_subactividades,
                'actividades_planificadas': self.actividades_planificadas,
                'actividades_sin_planificar': self.actividades_sin_planificar,
                'porcentaje_planificacion': self.porcentaje_planificacion,
                'total_presupuesto': float(self.total_presupuesto)
            },
            'timestamps': {
                'creado_el': self.creado_el.isoformat() if self.creado_el else None,
                'actualizado_el': self.actualizado_el.isoformat() if self.actualizado_el else None
            }
        }



auditlog.register(
    PlanificacionPei,
    include_fields=[
        'datos_tabla',
        'configuracion',
        'version',
        'creado_por',
        'actualizado_por'
    ],
    exclude_fields=['history', 'actualizado_el', 'creado_el', 'id'],
    mapping_fields={
        'datos_tabla': 'Actividades',
        'configuracion': 'Configuración',
        'version': 'Versión',
        'creado_por': 'Creado por',
        'actualizado_por': 'Modificado por'
    },
    serialize_data=True
)