from django.db import models




class SolicitudFondos(models.Model):
    id = models.AutoField(primary_key=True)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=True, null=True)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=True, null=True)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud')
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud')
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=True, null=True)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=True, null=True)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=True, null=True)
    idUsuario = models.IntegerField()
    idActividad = models.IntegerField()

    def __str__(self):
        return f"Solicitud de fondos #{self.id}"

    class Meta:
        db_table = 'spme_solicitud_fondos'
        verbose_name = 'Solicitud_fondos'
        verbose_name_plural = 'Solicitudes de fondos'

class RendicionCuentas(models.Model):
    id = models.AutoField(primary_key=True)
    cpteDiario = models.CharField(max_length=50, verbose_name='cpte_dinero', blank=True, null=True)
    fechaDesembolso = models.DateField(verbose_name='fecha_desembolso', blank=True, null=True)
    montoAsignado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='monto_asignado', blank=False, null=True)
    montoDescargado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='monto_descargado', blank=False, null=True)
    saldo = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='saldo', blank=False, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=True, null=True)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=True, null=True)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=True, null=True)
    validacionContador = models.BooleanField(default=False, verbose_name='contador_aprobacion')
    idContador = models.IntegerField(verbose_name='contador', blank=True, null=True)
    validacionAdministrador = models.BooleanField(default=False, verbose_name='administrador_aprobacion')
    idAdministrador = models.IntegerField(verbose_name='administrador', blank=True, null=True)
    idUsuario = models.IntegerField(blank=True, null=True)
    idActividad = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Solicitud de fondos #{self.id}"

    class Meta:
        db_table = 'spme_rendicion_cuentas'
        verbose_name = 'Rendicion_cuentas'
        verbose_name_plural = 'Rendiciones de cuentas'

class SolicitudReembolso(models.Model):
    id = models.AutoField(primary_key=True)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=True, null=True)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=True, null=True)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=True, null=True)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=True, null=True)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=True, null=True)
    idUsuario = models.IntegerField(blank=True, null=True)
    idActividad = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Solicitud de fondos #{self.id} - {self.fecha_solicitud}"

    class Meta:
        db_table = 'spme_solicitud_reembolso'
        verbose_name = 'Solicitud_reembolso'
        verbose_name_plural = 'Solicitudes de reembolso'

class SolicitudViaje (models.Model):
    id = models.AutoField(primary_key=True)
    evento = models.CharField(max_length=350, verbose_name='evento', blank=True, null=True)
    fechaInicio = models.DateField(verbose_name='fecha_inicio', blank=True, null=True)
    fechaFin = models.DateField(verbose_name='fecha_fin', blank=True, null=True)
    lugarEvento = models.CharField(max_length=50, verbose_name='lugar_evento', blank=True, null=True)
    institucionesParticipantes = models.CharField(max_length=250, verbose_name='instituciones',blank=True, null=True)
    organizador = models.CharField(max_length=150, verbose_name='organizador', blank=True, null=True)
    quienCubreGastos = models.TextField(max_length=350, verbose_name='quien_cubre_gastos', blank=True, null=True)
    justificacionAsistencia = models.TextField(max_length=500, verbose_name='justificacion_asistencia', blank=True, null=True)
    fondosUnitas = models.TextField(max_length=350, verbose_name='fondos_unitas', blank=True, null=True)
    tareasPrevias = models.TextField(max_length=350, verbose_name='tareas_previas', blank=True, null=True)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado', blank=True, null=True)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion', blank=True, null=True)
    idResponsable = models.IntegerField(verbose_name='responsable', blank=True, null=True)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion',)
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=True, null=True)
    idUsuario = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"Solicitud de fondos #{self.id}"

    class Meta:
        db_table = 'spme_solicitud_viaje'
        verbose_name = 'Solicitud_viaje'
        verbose_name_plural = 'Solicitudes de viajes'

class SolicitudPagoDirecto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, verbose_name='nombre')
    paterno = models.CharField(max_length=50, verbose_name='paterno')
    materno = models.CharField(max_length=50, verbose_name='materno')
    ci = models.CharField(max_length=15, verbose_name='ci')
    banco = models.CharField(max_length=50, verbose_name='banco')
    numeroCuenta = models.CharField(max_length=50, verbose_name='numero cuenta')
    cargo = models.CharField(max_length=30, verbose_name='cargo')
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=True, null=True)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=True, null=True)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=True, null=True)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=True, null=True)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=True, null=True)
    idUsuario = models.IntegerField(blank=True, null=True)
    idActividad = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Solicitud de fondos #{self.id}"

    class Meta:
        db_table = 'spme_solicitud_pago_directo'
        verbose_name = 'Solicitud_pago_directo'
        verbose_name_plural = 'Solicitudes de pago directo'
