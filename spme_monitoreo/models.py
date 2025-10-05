from django.db import models
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad
from polymorphic.models import PolymorphicModel

class FormaPago(models.Model):
    codigo = models.CharField(max_length=10, blank=True, null=True)
    formaPago = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        verbose_name='Forma de Pago'
        verbose_name_plural='Formas de Pago'

    def __str__(self):
        return self.codigo    

#Formulario de solicitud de fondos
class SolicitudFondos(models.Model):
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='Detalle destino de fondos', blank=True, null=True)
    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitudes_fondo',
        verbose_name='Forma de Pago',
        null=True,
        blank=True,
    )
    lugarSolicitud = models.TextField(blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='Fecha de la solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Monto Solicitado', blank=True, null=True)
    #Actividad
    fechaRealizacionActividad = models.DateField(verbose_name="Fecha de realizacion del actividad", blank=True, null=True)
    #Discriminador
    bloquearIconosSolFondos = models.BooleanField(default=True)
    #Validacion
    validacionResponsable = models.BooleanField(default=False)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_responsable_solicitud',
        null=True,
        blank=True,
    )
    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_solicitud',
        null=True,
        blank=True,
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_solicitud',
        null=True,
        blank=True,
    )
    actividad = models.ForeignKey(
        Actividad, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_solicitud',
        null=True,
        blank=True,
    )

    tarea = models.ForeignKey(
        TareaActividad,
        on_delete=models.SET_NULL,
        related_name='tarea_solicitud',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Fondos'
        verbose_name_plural = 'Solicitudes de Fondos'


#Solicitud de reembolso
class SolicitudReembolso(models.Model):
    #Datos del formulario
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='Detalle destino de fondos', blank=True, null=True)
    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitud_reembolso',
        blank=True,
        null=True,
    )
    lugarSolicitud = models.CharField(max_length=50, verbose_name='Lugar solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='Fecha solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='Monto solicitado',blank=True, null=True)


    #Campos Extra
    descripcionReposicion = models.TextField(blank=True,null=True)


    #discriminador
    bloquearIconos = models.BooleanField(default=True)

    #Validaciones
    validacionResponsable = models.BooleanField(default=False)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_responsable_reembolso',
        null=True,
        blank=True,
    )

    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_reembolso',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_reembolso',
        null=True,
        blank=True,
    )

    actividad = models.ForeignKey(
        Actividad, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_reembolso',
        null=True,
        blank=True,
    )

    tarea = models.ForeignKey(
        TareaActividad,
        on_delete=models.SET_NULL,
        related_name='tarea_reembolso',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Reembolso'
        verbose_name_plural = 'Solicitudes de Reembolso'

#Solicitud de viaje
class SolicitudViaje (models.Model):
    #Datos del formulario
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    evento = models.TextField(verbose_name='evento', blank=True, null=True)
    lugarEvento = models.CharField(max_length=50, verbose_name='Lugar del evento', blank=True, null=True)
    institucionesParticipantes = models.TextField(verbose_name='Instituciones participantes',blank=True, null=True)
    organizador = models.TextField(verbose_name='Organizador', blank=True, null=True)
    quienCubreGastos = models.TextField(verbose_name='quien_cubre_gastos', blank=True, null=True)
    justificacionAsistencia = models.TextField(verbose_name='justificacion_asistencia', blank=True, null=True)
    fondosUnitas = models.TextField( verbose_name='fondos_unitas', blank=True, null=True)
    tareasPrevias = models.TextField( verbose_name='tareas_previas', blank=True, null=True)

    #Bloquear iconos
    bloquearIconos = models.BooleanField(default=True)

    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitud_viaje_fondo',
        null=True,
        blank=True,
    )
    montoSolicitado = models.DecimalField(max_digits=12,decimal_places=2,verbose_name ='monto_solicitado', blank=True, null=True)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)

    #Campos extra
    fechaEvento = models.DateField(blank=True, null=True)
    detalleGasto = models.JSONField(blank=True, null=True)

    #Validaciones
    validacionResponsable = models.BooleanField(default=False)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_responsable_sol_viaje',
        null=True,
        blank=True,
    )

    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_sol_viaje',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_sol_viaje',
        null=True,
        blank=True,
    )

    actividad = models.ForeignKey(
        Actividad, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_sol_viaje',
        null=True,
        blank=True,
    )

    tarea = models.ForeignKey(
        TareaActividad,
        on_delete=models.SET_NULL,
        related_name='tarea_solicitud_sol_viaje',
        null=True,
        blank=True,
    )      
    
    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Viaje'
        verbose_name_plural = 'Solicitudes de Viaje'


class SolicitudPagoDirecto(models.Model):
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    nombre = models.CharField(max_length=50, verbose_name='nombre', blank=True, null=True)
    paterno = models.CharField(max_length=50, verbose_name='paterno', blank=True, null=True)
    materno = models.CharField(max_length=50, verbose_name='materno', blank=True, null=True)
    ci = models.CharField(max_length=15, verbose_name='ci', blank=True, null=True)
    banco = models.CharField(max_length=50, verbose_name='banco', blank=True, null=True)
    numeroCuenta = models.CharField(max_length=50, verbose_name='numero cuenta', blank=True, null=True)
    cargo = models.CharField(max_length=30, verbose_name='cargo', blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=True, null=True)

    #Discriminador
    bloquearIconos = models.BooleanField(default=True)

    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitud_pago_directo',
        null=True,
        blank=True,
    )

    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=True, null=True)

     #Validaciones
    validacionResponsable = models.BooleanField(default=False)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_responsable_sol_pago_directo',
        null=True,
        blank=True,
    )

    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_sol_pago_directo',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_sol_pago_directo',
        null=True,
        blank=True,
    )

    actividad = models.ForeignKey(
        Actividad, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_sol_pago_directo',
        null=True,
        blank=True,
    ) 

    tarea = models.ForeignKey(
        TareaActividad,
        on_delete=models.SET_NULL,
        related_name='tarea_solicitud_sol_pago_directo',
        null=True,
        blank=True,
    )  
    
    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Pago Directo'
        verbose_name_plural = 'Solicitudes de Pago Directo'


#Rendicion de cuentas
class RendicionCuentas(models.Model):
    #Datos del formulario
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    cpteDiario = models.CharField(max_length=100, blank=True, null=True)
    fechaDesembolso = models.DateField(verbose_name='Fecha de desembolso', blank=True, null=True)
    montoAsignado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Monto asignado', blank=True, null=True)
    montoDescargado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Monto Descargado', blank=False, null=True)
    saldo = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Saldo', blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='Detalle destino de fondos', blank=True, null=True)
    #Informacion sobre Actividades y Tareas
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        related_name='rendicion_cuentas_actividad',
        null=True,
        blank=True,
    )
    fechaActividad = models.DateField(verbose_name='Fecha de la actividad', blank=True, null=True)
    descripcionActividad = models.TextField(blank=True, null=True)
    lugarActividad = models.TextField(blank=True, null=True)
    tarea = models.ForeignKey(
        TareaActividad,
        on_delete=models.SET_NULL,
        related_name='rendicion_cuentas_tarea_actividad',
        null=True,
        blank=True,
    )
    #Discriminador
    bloquearIconos = models.BooleanField(default=True)
    #Validaciones
    validacionResponsable = models.BooleanField(default=False)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_responsable_rendicion',
        null=True,
        blank=True,
    )
    validacionCoordinador = models.BooleanField(default=False)    
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_rendicion',
        null=True,
        blank=True,
    )

    validacionContador = models.BooleanField(default=False)
    contador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_contador_rendicion',
        null=True,
        blank=True,
    )

    validacionAdministrador = models.BooleanField(default=False)
    administrador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usario_administrador_rendicion',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_rendicion',
        null=True,
        blank=True,
    )
    #Solicitud
    solicitudFondos = models.ForeignKey(
        SolicitudFondos,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_fondos',
        null=True,
        blank=True,
    )
    solicitudReembolso = models.ForeignKey(
        SolicitudReembolso,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_reembolso',
        null=True,
        blank=True,
    )
    solicitudViaje = models.ForeignKey(
        SolicitudViaje,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_viaje',
        null=True,
        blank=True,
    )
    solicitudPagoDirecto = models.ForeignKey(
        SolicitudPagoDirecto,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_pago_directo',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Rendicion de cuentas'
        verbose_name_plural = 'Rendiciones de cuentas'



#Informe de Actividad
class InformeActividad(models.Model):
    numeroInforme = models.CharField(max_length=50, blank=True, null=True)
    contribucionesProyecto = models.JSONField(blank=True, null=True)
    contribucionesActividad = models.JSONField(blank=True, null=True)
    informaObjetivoActividad = models.TextField(blank=True, null=True)
    reporteTipo = models.CharField(max_length=100, blank=True, null=True)
    indicador = models.JSONField(blank=True, null=True)
    herramientaEvaluacion = models.TextField(blank=True, null=True)
    descripcionMediosVerificacion = models.TextField(blank=True, null=True)
    comentariosRecomendacion = models.TextField(blank=True, null=True)
    presupuestoEjecutado = models.JSONField(blank=True, null=True)

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        related_name='actividad_informe_actividad',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.numeroInforme
    
    class Meta:
        verbose_name = 'Informe Actividad'
        verbose_name_plural = 'Informes de Actividad'

 
#Informe Base
class InformeBase(PolymorphicModel):
    numeroInforme = models.CharField(max_length=50, blank=True, null=True)
    fecha_ejecucion = models.DateField(blank=True, null=True)
    contribucion_proyecto = models.JSONField(blank=True, null=True)
    avance_indicadores = models.TextField(blank=True, null=True)
    informacion_cuantitativa = models.TextField(blank=True, null=True)
    herramientas_evaluacion = models.TextField(blank=True, null=True)
    medios_verificacion = models.TextField(blank=True, null=True)
    comentarios_recomendaciones = models.TextField(blank=True, null=True)
    presupuesto_planificado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Presupuesto planificado', blank=True, null=True)
    presupuesto_ejecutado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Presupuesto ejecutado', blank=True, null=True)
         
    class Meta:
        verbose_name = 'Informe Base actividada y subactividad'
        verbose_name_plural = 'Informes Base actividad y subactividad'

#Informe de actividad
class InfActividad(InformeBase):
    objetivo_actividad = models.TextField(blank=True, null=True)
    informe_objetivo_actividad = models.TextField(blank=True, null=True)
    tipo_actividad = models.CharField(max_length=255, blank=True, null=True)
    procedencia_fondos = models.JSONField(blank=True, null=True)

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        related_name='activida_informes_de_actividad',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Informe de Actividad'
        verbose_name_plural = 'Informes de actividades'


#Informe de tarea
class InfTarea(InformeBase):
    objetivo_actividad = models.TextField(blank=True, null=True)
    informe_objetivo_actividad = models.TextField(blank=True, null=True)
    tipo_actividad = models.CharField(max_length=255, blank=True, null=True)
    desglose_presupuesto = models.JSONField(blank=True, null=True)

    tarea = models.ForeignKey(
        TareaActividad,
        on_delete=models.SET_NULL,
        related_name='activida_informes_de_actividad',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Informe de Tarea'
        verbose_name_plural = 'Informes de Tareas'





