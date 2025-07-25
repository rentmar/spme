from django.db import models

class SolicitudFondos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, verbose_name='nombre')
    paterno = models.CharField(max_length=50, verbose_name='paterno')
    materno = models.CharField(max_length=50, verbose_name='materno')
    cargo = models.CharField(max_length=50, verbose_name='cargo')
    aprobador = models.CharField(max_length=50, verbose_name='aprobador')
    descripcion = models.TextField(max_length=350, verbose_name='descripcion', blank=False, null=False)
    fechaRealizacion = models.DateField(verbose_name='fecha_realizacion')
    objetivoActividad = models.TextField(max_length=350, verbose_name='objetivo_actividad', blank=False, null=False)
    fuenteFinanciamiento = models.CharField(max_length=50, verbose_name='fuente_financiamiento')
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=False, null=False)
    beneficiario = models.TextField(max_length=50, verbose_name='beneficiarios', blank=False, null=False)
    documentoIdentidadBeneficiario = models.CharField(max_length=20, verbose_name='documento_identidad_beneficiario')
    banco = models.CharField(max_length=50, verbose_name='banco')
    numeroCuenta = models.CharField(max_length=40, verbose_name='numero_cuenta')
    tipoCuenta = models.CharField(max_length=20, verbose_name='tipo_cuenta')
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud')
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud')
    montoSolicitado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='monto_solicitado')
    responsableAprobacion = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    responsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    coordinadorAprobacion = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    coordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)

    def __str__(self):
        return self.nombre+' ' + self.paterno + ' ' + self.materno

    class Meta:
        db_table = 'spme_solicitud_fondos'
        verbose_name = 'Solicitud_fondos'
        verbose_name_plural = 'Solicitudes de fondos'

class RendicionCuentas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, verbose_name='nombre')
    paterno = models.CharField(max_length=50, verbose_name='paterno')
    materno = models.CharField(max_length=50, verbose_name='materno')
    documentoIdentidad = models.CharField(max_length=20, verbose_name='documento_identidad')
    cargo = models.CharField(max_length=50, verbose_name='cargo')
    numeroFormulario = models.CharField(max_length=20, verbose_name='numero_formulario')
    cpteDiario = models.CharField(max_length=50, verbose_name='cpte_dinero')
    fechaDesembolso = models.DateField(verbose_name='fecha_desembolso')
    montoAsignado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='monto_asignado')
    montoDescargado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='monto_descargado')
    saldoRestante = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='saldo_restante')
    fuenteFinanciamiento = models.CharField(max_length=50, verbose_name='fuente_financiamiento')
    descripcion = models.TextField(max_length=350, verbose_name='descripcion', blank=False, null=False)
    fechaRealizacion = models.DateField(verbose_name='fecha_realizacion')
    lugarActividad = models.CharField(max_length=50, verbose_name='lugar_actividad')
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=False, null=False)
    responsableAprobacion = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    responsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    coordinadorAprobacion = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    coordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)
    contadorAprobacion = models.BooleanField(default=False, verbose_name='contador_aprobacion')
    contador = models.IntegerField(verbose_name='contador', blank=False, null=False)
    administradorAprobacion = models.BooleanField(default=False, verbose_name='administrador_aprobacion')
    administrador = models.IntegerField(verbose_name='administrador', blank=False, null=False)

    def __str__(self):
        return self.nombre+' ' + self.paterno + ' ' + self.materno

    class Meta:
        db_table = 'spme_rendicion_cuentas'
        verbose_name = 'Rendicion_cuentas'
        verbose_name_plural = 'Rendiciones de cuentas'

class SolicitudReembolso(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, verbose_name='nombre')
    paterno = models.CharField(max_length=50, verbose_name='paterno')
    materno = models.CharField(max_length=50, verbose_name='materno')
    cargo = models.CharField(max_length=50, verbose_name='cargo')
    aprobador = models.CharField(max_length=50, verbose_name='aprobador')
    descripcion = models.TextField(max_length=350, verbose_name='descripcion', blank=False, null=False)
    fechaRealizacion = models.DateField(verbose_name='fecha_realizacion')
    objetivoActividad = models.TextField(max_length=350, verbose_name='objetivo_actividad', blank=False, null=False)
    fuenteFinanciamiento = models.CharField(max_length=50, verbose_name='fuente_financiamiento')
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=False, null=False)
    beneficiario = models.TextField(max_length=350, verbose_name='beneficiarios', blank=False, null=False)
    documentoIdentidadBeneficiario = models.CharField(max_length=20, verbose_name='documento_identidad_beneficiario')
    banco = models.CharField(max_length=50, verbose_name='banco')
    numeroCuenta = models.CharField(max_length=40, verbose_name='numero_cuenta')
    tipoCuenta = models.CharField(max_length=20, verbose_name='tipo_cuenta')
    lugarSolicitud = models.CharField(max_length=50, verbose_name='lugar_solicitud')
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud')
    montoSolicitado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='monto_solicitado')
    responsableAprobacion = models.BooleanField(default=False, verbose_name='responsable_aprobacion')
    responsable = models.IntegerField(verbose_name='responsable', blank=False, null=False)
    coordinadorAprobacion = models.BooleanField(default=False, verbose_name='coordinador_aprobacion')
    coordinador = models.IntegerField(verbose_name='coordinador', blank=False, null=False)

    def __str__(self):
        return self.nombre+' ' + self.paterno + ' ' + self.materno

    class Meta:
        db_table = 'spme_solicitud_reembolso'
        verbose_name = 'Solicitud_reembolso'
        verbose_name_plural = 'Solicitudes de reembolso'
