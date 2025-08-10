from django.db import models

class SolicitudFondos(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.TextField(max_length=350, verbose_name='descripcion', blank=False, null=False)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=False, null=False)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=False, null=False)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud')
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud')
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=False, null=False)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)
    idUsuario = models.IntegerField()
    idActividad = models.IntegerField()

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'spme_solicitud_fondos'
        verbose_name = 'Solicitud_fondos'
        verbose_name_plural = 'Solicitudes de fondos'

class RendicionCuentas(models.Model):
    id = models.AutoField(primary_key=True)
    cpteDiario = models.CharField(max_length=50, verbose_name='cpte_dinero')
    fechaDesembolso = models.DateField(verbose_name='fecha_desembolso')
    descripcion = models.TextField(max_length=350, verbose_name='descripcion', blank=False, null=False)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=False, null=False)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)
    validacionContador = models.BooleanField(default=False, verbose_name='contador_aprobacion')
    idContador = models.IntegerField(verbose_name='contador', blank=False, null=False)
    validacionAdministrador = models.BooleanField(default=False, verbose_name='administrador_aprobacion')
    idAdministrador = models.IntegerField(verbose_name='administrador', blank=False, null=False)
    idUsuario = models.IntegerField()
    idActividad = models.IntegerField()

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'spme_rendicion_cuentas'
        verbose_name = 'Rendicion_cuentas'
        verbose_name_plural = 'Rendiciones de cuentas'

class SolicitudReembolso(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.TextField(max_length=350, verbose_name='descripcion', blank=False, null=False)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=False, null=False)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=False, null=False)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud')
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud')
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=False, null=False)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)
    idUsuario = models.IntegerField()
    idActividad = models.IntegerField()

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'spme_solicitud_reembolso'
        verbose_name = 'Solicitud_reembolso'
        verbose_name_plural = 'Solicitudes de reembolso'

class SolicitudViaje (models.Model):
    id = models.AutoField(primary_key=True)
    evento = models.CharField(max_length=350, verbose_name='evento', blank=False, null=False)
    fechaInicio = models.DateField(verbose_name='fecha_inicio')
    fechaFin = models.DateField(verbose_name='fecha_fin')
    lugarEvento = models.CharField(max_length=50, verbose_name='lugar_evento')
    institucionesParticipante = models.CharField(max_length=250, verbose_name='instituciones')
    organizador = models.CharField(max_length=150, verbose_name='organizador')
    quienCubreGastos = models.TextField(max_length=350, verbose_name='quien_cubre_gastos', blank=False, null=False)
    justificacionAsistencia = models.TextField(max_length=500, verbose_name='justificacion_asistencia', blank=False, null=False)
    fondosUnitas = models.TextField(max_length=350, verbose_name='fondos_unitas', blank=False, null=False)
    tareasPrevias = models.TextField(max_length=350, verbose_name='tareas_previas', blank=False, null=False)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=False, null=False)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=False, null=False)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud')
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud')
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)
    idUsuario = models.IntegerField()
    
    def __str__(self):
        return self.id

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
    descripcion = models.TextField(max_length=350, verbose_name='descripcion', blank=False, null=False)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=False, null=False)
    formaPago = models.IntegerField(verbose_name='forma_pago', blank=False, null=False)
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud')
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud')
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=False, null=False)
    validacionResponsable = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    idResponsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    validacionCoordinador = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    idCoordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)
    idUsuario = models.IntegerField()
    idActividad = models.IntegerField()

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'spme_solicitud_pago_directo'
        verbose_name = 'Solicitud_pago_directo'
        verbose_name_plural = 'Solicitudes de pago directo'
