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

from django.db import models
from django.db.models import Max
from django.utils import timezone

class PlanificacionPei(models.Model):
    """
    Modelo principal para planificación PEI.
    La versión se incrementa automáticamente por cada PEI.
    """
    
    # -----------------------------------------------------------------
    # 1. RELACIONES PRINCIPALES
    # -----------------------------------------------------------------
    pei = models.ForeignKey(
        Pei,
        on_delete=models.CASCADE,
        related_name='planificacion_pei',
        verbose_name='PEI Relacionado',
        help_text='Cada PEI puede tener multiples planificaciones'
    )
    
    # -----------------------------------------------------------------
    # 2. DATOS DEL FRONTEND (VUE COMPONENT)
    # -----------------------------------------------------------------
    datos_tabla_actual = models.JSONField(
        verbose_name='Datos de actividades Originales',
        default=list,
        help_text='Estructura JSON completa de actividades, su estado y planificacion. Actual.',
        blank=True,
        null=True
    )

    datos_tabla_actualizado = models.JSONField(
        verbose_name='Datos de actividades Actualizadas',
        default=list,
        help_text='Estructura JSON completa de actividades, su estado y planificacion. Actualizado.',
        blank=True,
        null=True
    )

    cambios_efectuados = models.JSONField(
        verbose_name='Campos actualizados',
        default=list,
        help_text='Datos de los cambios efectuados',
        blank=True,
        null=True
    )
    
    configuracion = models.JSONField(
        verbose_name='Configuración de tabla',
        default=dict,
        help_text='Columnas, fórmulas, formatos de visualización',
        blank=True,
        null=True
    )
    
    # -----------------------------------------------------------------
    # 3. CONTROL DE VERSIONES (MODIFICADO)
    # -----------------------------------------------------------------
    version = models.IntegerField(
        default=1,
        verbose_name='Versión',
        help_text='Número de versión, se incrementa automáticamente al crear nueva planificación para el mismo PEI'
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
        help_text='Calculado automáticamente de datos_tabla_actualizado'
    )
    
    total_subactividades = models.IntegerField(
        default=0,
        verbose_name='Total de subactividades',
        help_text='Calculado automáticamente de datos_tabla_actualizado'
    )
    
    total_presupuesto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Presupuesto total',
        help_text='Suma de presupuestos de actividades principales de datos_tabla_actualizado'
    )
    
    actividades_planificadas = models.IntegerField(
        default=0,
        verbose_name='Actividades planificadas',
        help_text='Actividades con fechas de inicio y fin definidas en datos_tabla_actualizado'
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
        ordering = ['pei', '-version']  # Ordenar por PEI y luego por versión descendente
        unique_together = ['pei', 'version']  # Cada PEI tiene versiones únicas
        indexes = [
            models.Index(fields=['pei', 'version']),  # Índice compuesto para búsquedas rápidas
            models.Index(fields=['pei']),
            models.Index(fields=['version']),
            models.Index(fields=['creado_por']),
            models.Index(fields=['actualizado_por']),
            models.Index(fields=['creado_el']),
            models.Index(fields=['actualizado_el']),
        ]
    
    def __str__(self):
        return f"PEI {self.pei.id} - Planificación v{self.version}"
    
    # -----------------------------------------------------------------
    # MÉTODOS PRINCIPALES - MODIFICADOS
    # -----------------------------------------------------------------
    
    def save(self, *args, **kwargs):
        """
        Sobreescribir save para:
        1. Asignar versión secuencial por PEI
        2. Calcular estadísticas automáticas
        3. Manejar lógica de usuario
        """
        es_nuevo = not self.pk
        
        if es_nuevo:
            # Para nueva planificación: obtener última versión del mismo PEI y sumar 1
            ultima_version = PlanificacionPei.objects.filter(
                pei=self.pei
            ).aggregate(Max('version'))['version__max']
            
            if ultima_version:
                self.version = ultima_version + 1
            else:
                self.version = 1  # Primera versión para este PEI
            
            # Para nuevas planificaciones, establecer creado_por si no está definido
            if not self.creado_por and hasattr(self, 'request_user'):
                self.creado_por = self.request_user
        
        # Para actualizaciones (no nuevas), mantener la versión actual
        # pero actualizar el usuario de modificación
        elif not es_nuevo and hasattr(self, 'request_user'):
            self.actualizado_por = self.request_user
        
        # Calcular estadísticas antes de guardar
        self._calcular_estadisticas()
        
        # Llamar al save original
        super().save(*args, **kwargs)
    
    def _calcular_estadisticas(self):
        """
        Calcular todos los campos automáticos basados en datos_tabla_actualizado.
        """
        try:
            datos = self.datos_tabla_actualizado or []
            
            actividades = 0
            subactividades = 0
            presupuesto_total = 0.0
            planificadas = 0
            
            for item in datos:
                nivel = item.get('nivel', 0)
                
                if nivel == 0:  # Actividad principal
                    actividades += 1
                    
                    if item.get('fecha_inicio_plan') and item.get('fecha_fin_plan'):
                        planificadas += 1
                    
                    try:
                        presupuesto = float(item.get('presupuesto', 0) or 0)
                        presupuesto_total += presupuesto
                    except (ValueError, TypeError):
                        pass
                    
                    if 'subactividades' in item and isinstance(item['subactividades'], list):
                        subactividades += len(item['subactividades'])
                
                elif nivel == 1:  # Subactividad directa
                    subactividades += 1
            
            self.total_actividades = actividades
            self.total_subactividades = subactividades
            self.total_presupuesto = presupuesto_total
            self.actividades_planificadas = planificadas
            
        except Exception as e:
            print(f"⚠️ Error calculando estadísticas para PEI {self.pei.id} v{self.version}: {e}")
    
    # -----------------------------------------------------------------
    # MÉTODOS DE GESTIÓN DE VERSIONES
    # -----------------------------------------------------------------
    
    @classmethod
    def obtener_ultima_version(cls, pei_id):
        """
        Obtener la última versión para un PEI específico.
        
        Args:
            pei_id (int): ID del PEI
            
        Returns:
            PlanificacionPei or None: Última versión o None si no existe
        """
        try:
            return cls.objects.filter(pei_id=pei_id).latest('version')
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def obtener_todas_versiones(cls, pei_id):
        """
        Obtener todas las versiones de un PEI ordenadas por versión.
        
        Args:
            pei_id (int): ID del PEI
            
        Returns:
            QuerySet: Todas las versiones ordenadas por versión ascendente
        """
        return cls.objects.filter(pei_id=pei_id).order_by('version')
    
    @classmethod
    def crear_nueva_version(cls, pei_id, usuario, datos_tabla_actualizado=None, configuracion=None):
        """
        Crear una nueva versión para un PEI basada en la última versión.
        
        Args:
            pei_id (int): ID del PEI
            usuario: Usuario que crea la nueva versión
            datos_tabla_actualizado (optional): Nuevos datos de tabla
            configuracion (optional): Nueva configuración
            
        Returns:
            PlanificacionPei: La nueva versión creada
        """
        # Obtener la última versión
        ultima_version = cls.obtener_ultima_version(pei_id)
        
        if not ultima_version:
            # Si no existe versión anterior, crear la primera
            return cls.objects.create(
                pei_id=pei_id,
                datos_tabla_actual=[],
                datos_tabla_actualizado=datos_tabla_actualizado or [],
                cambios_efectuados=[],
                configuracion=configuracion or {},
                creado_por=usuario,
                actualizado_por=usuario
            )
        
        # Crear nueva versión basada en la última
        nueva_version = cls.objects.create(
            pei_id=pei_id,
            # Mantener datos originales de la última versión
            datos_tabla_actual=ultima_version.datos_tabla_actual,
            # Actualizar con nuevos datos o copiar los existentes
            datos_tabla_actualizado=datos_tabla_actualizado or ultima_version.datos_tabla_actualizado.copy(),
            # Inicializar cambios_efectuados como lista vacía
            cambios_efectuados=[],
            configuracion=configuracion or ultima_version.configuracion.copy(),
            creado_por=ultima_version.creado_por,  # Mantener creador original
            actualizado_por=usuario,               # Nuevo actualizador
            # La versión se asignará automáticamente en save()
        )
        
        return nueva_version
    
    def crear_version_siguiente(self, usuario, datos_tabla_actualizado=None, configuracion=None):
        """
        Crear una nueva versión basada en esta versión actual.
        
        Args:
            usuario: Usuario que crea la nueva versión
            datos_tabla_actualizado (optional): Nuevos datos de tabla
            configuracion (optional): Nueva configuración
            
        Returns:
            PlanificacionPei: La nueva versión creada
        """
        return self.__class__.crear_nueva_version(
            pei_id=self.pei_id,
            usuario=usuario,
            datos_tabla_actualizado=datos_tabla_actualizado or self.datos_tabla_actualizado.copy(),
            configuracion=configuracion or self.configuracion.copy()
        )
    
    # -----------------------------------------------------------------
    # MÉTODOS DE UTILIDAD PARA CONSULTAS
    # -----------------------------------------------------------------
    
    def obtener_resumen_auditoria(self):
        """
        Obtener resumen completo de auditoría para esta planificación.
        """
        return {
            'pei': {
                'id': self.pei.id,
                'titulo': self.pei.titulo,
            },
            'version': {
                'actual': self.version,
                'total_versiones': PlanificacionPei.objects.filter(pei=self.pei).count()
            },
            'creacion': {
                'usuario': self._obtener_info_usuario(self.creado_por),
                'fecha': self.creado_el,
                'version': 1
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
    
    def _obtener_info_usuario(self, usuario):
        """
        Obtener información estructurada de un usuario.
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
    # PROPIEDADES CALCULADAS
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
    def es_ultima_version(self):
        """¿Es esta la última versión del PEI?"""
        ultima_version = self.__class__.obtener_ultima_version(self.pei_id)
        return ultima_version and ultima_version.id == self.id
    
    def to_dict(self):
        """
        Convertir modelo a diccionario para serialización.
        """
        return {
            'id': self.id,
            'pei_id': self.pei.id,
            'pei_titulo': self.pei.titulo,
            'datos_tabla_actual': self.datos_tabla_actual,
            'datos_tabla_actualizado': self.datos_tabla_actualizado,
            'cambios_efectuados': self.cambios_efectuados,
            'configuracion': self.configuracion,
            'version': {
                'numero': self.version,
                'es_ultima': self.es_ultima_version,
                'total_versiones': PlanificacionPei.objects.filter(pei=self.pei).count()
            },
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
        'datos_tabla_actual',
        'datos_tabla_actualizado',
        'cambios_efectuados',
        'configuracion',
        'version',
        'creado_por',
    ],
    exclude_fields=['history', 'actualizado_el', 'creado_el', 'id'],
    mapping_fields={
        'datos_tabla_actual': 'Actividades',
        'datos_tabla_actualizado': 'Actividades current',
        'cambios_efectuados': 'Cambios efectuados',
        'configuracion': 'Configuración',
        'version': 'Versión',
        'creado_por': 'Creado por',
        'actualizado_por': 'Modificado por'
    },
    serialize_data=True
)