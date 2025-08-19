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
    fechaInicio = models.DateField(verbose_name='fecha_inicio', blank=True, null=True)
    fechaFin = models.DateField(verbose_name='fecha_fin', blank=True, null=True)
    lugarEvento = models.CharField(max_length=50, verbose_name='Lugar del evento', blank=True, null=True)
    institucionesParticipantes = models.TextField(verbose_name='Instituciones participantes',blank=True, null=True)
    organizador = models.TextField(verbose_name='Organizador', blank=True, null=True)
    quienCubreGastos = models.TextField(verbose_name='quien_cubre_gastos', blank=True, null=True)
    justificacionAsistencia = models.TextField(verbose_name='justificacion_asistencia', blank=True, null=True)
    fondosUnitas = models.TextField( verbose_name='fondos_unitas', blank=True, null=True)
    tareasPrevias = models.TextField( verbose_name='tareas_previas', blank=True, null=True)

    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitud_viaje_fondo',
        null=True,
        blank=True,
    )
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado', blank=True, null=True)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)

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
    SolicitudReembolso = models.ForeignKey(
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
