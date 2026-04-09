from django.db import models
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad
from spme_estructuracion_pei.models import ActividadPei, TareaActividadPei
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

    descripcion_actividad = models.TextField(verbose_name='Descripción de la actividad', blank=True, null=True)
    objetivo_actividad = models.TextField(verbose_name='Objetivo de la actividad', blank=True, null=True)
    datos_forma_pago = models.JSONField(verbose_name='Datos de forma de pago', blank=True, null=True)
    #Discriminador
    bloquearIconosSolFondos = models.BooleanField(default=True)
    #Validacion
    validacionResponsable = models.BooleanField(default=False)
    contador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_contador_solicitud',
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

    # Campos automáticos de Django (si usas auto_now_add y auto_now)
    # created_at = models.DateTimeField(auto_now_add=True)  # Si existe
    # updated_at = models.DateTimeField(auto_now=True)      # Si existe

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
    montoSolicitado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Monto solicitado', blank=True, null=True)
    descripcion_actividad = models.TextField(blank=True, null=True, verbose_name='Descripción de la actividad')
    objetivo_actividad = models.TextField(blank=True, null=True, verbose_name='Objetivo de la actividad')
    datos_forma_pago = models.JSONField(blank=True, null=True, verbose_name='Datos de forma de pago')
    fechaRealizacionActividad = models.DateField(blank=True, null=True, verbose_name='Fecha de realizacion del actividad')

    #Bloquear iconos
    bloquearIconos = models.BooleanField(default=True)
        
    #Validaciones
    # validacionContador = models.BooleanField(default=False)
    # contador = models.ForeignKey(
    #     Usuario,
    #     on_delete=models.SET_NULL,
    #     related_name='usuario_contador_reembolso',
    #     null=True,
    #     blank=True,
    # )

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

    def save(self, *args, **kwargs):
        # Normalizar codigo vacío a None
        if self.numeroFormulario == '':
            self.numeroFormulario = None
        
        # Si es una nueva solicitud sin código, guardar primero para obtener el ID
        is_new = not self.pk
        needs_codigo = not self.numeroFormulario and self.actividad
        
        # Guardar para obtener el ID si es necesario
        super().save(*args, **kwargs)
        
        # Generar código usando el ID único de la tarea
        if is_new and needs_codigo:
            numero_formateado = f"{self.pk:04d}"
            #self.numeroFormulario = f"SACT-{numero_formateado}/{self.actividad.codigo}"
            self.numeroFormulario = f"{self.actividad.codigo}- SR{numero_formateado}"
            # Guardar nuevamente con el código generado
            super().save(update_fields=['numeroFormulario'])   

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
    
    datos_forma_pago = models.JSONField(
        verbose_name='Datos de forma de pago', 
        blank=True, 
        null=True,
        help_text='Información de forma de pago (transferencia, otros, etc.)'
    ) 
    
    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Viaje'
        verbose_name_plural = 'Solicitudes de Viaje'


class SolicitudPagoDirecto(models.Model):
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=True, null=True)
    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitud_pago_directo',
        null=True,
        blank=True,
    )
    lugarSolicitud = models.TextField(blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=True, null=True)
    #Actividad
    fechaRealizacionActividad = models.DateField(verbose_name="Fecha de realizacion del actividad", blank=True, null=True)

    descripcion_actividad = models.TextField(blank=True, null=True, verbose_name='Descripción de la actividad')
    objetivo_actividad = models.TextField(blank=True, null=True, verbose_name='Objetivo de la actividad')
    datos_forma_pago = models.JSONField(verbose_name='Datos de forma de pago', blank=True, null=True)
    
    #Discriminador
    bloquearIconosSolFondos = models.BooleanField(default=True)
    
     #Validaciones
    validacionResponsable = models.BooleanField(default=False)
    contador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_contador_sol_pago_directo',
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
    fechaRendicion = models.DateField(verbose_name='Fecha de Rendición', auto_now_add=True, blank=True, null=True)
    descripcionActividad = models.TextField(blank=True, null=True)
    lugarActividad = models.TextField(blank=True, null=True)
    lugarRendicion = models.TextField(blank=True, null=True)
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
        related_name='usuario_administrador_rendicion',
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


#Informe de Actividades - Completo
class InformeActividadBase(PolymorphicModel):
    numeroInforme = models.CharField(max_length=50, blank=True, null=True)
    fechaEjecucion = models.DateField(blank=True, null=True)
    contribucionProyecto = models.JSONField(blank=True, null=True)
    avanceIndicadores = models.JSONField(blank=True, null=True)
    informacionCuantitativa = models.JSONField(blank=True, null=True)
    herramientasEvaluacion = models.JSONField(blank=True, null=True)
    mediosVerificacion = models.TextField(blank=True, null=True)
    comentariosRecomendaciones = models.TextField(blank=True, null=True)
    presupuestoPlanificado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Presupuesto planificado', blank=True, null=True)
    presupuestoEjecutado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Presupuesto ejecutado', blank=True, null=True)

    #Campos para seguimiento
    timestamp_registro = models.DateTimeField(
        auto_now_add=True,  # Se establece automáticamente al crear el registro
        verbose_name='Fecha y hora de registro',
        help_text='Fecha y hora en que se creó el registro',
        null=True,
        blank=True
    )
    timestamp_ultima_modificacion = models.DateTimeField(
        auto_now=True,  # Se actualiza automáticamente cada vez que se guarda
        verbose_name='Última modificación',
        help_text='Fecha y hora de la última modificación',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Informe Base actividada y subactividad principal'
        verbose_name_plural = 'Informes Base actividad y subactividad principal'

class InformeActividadPrincipal(InformeActividadBase):
    objetivoActividad = models.TextField(blank=True, null=True)
    informeObjetivoActividad = models.TextField(blank=True, null=True)
    tipoActividad = models.CharField(max_length=255, blank=True, null=True)
    reporteTipo = models.TextField(blank=True, null=True)
    procedenciaFondos = models.JSONField(blank=True, null=True)
    observacionesPresupuesto = models.TextField(blank=True, null=True)  
    archivosCuantitativos = models.JSONField(blank=True, null=True)  
    herramientasArchivos = models.JSONField(blank=True, null=True)  
    mediosArchivos = models.JSONField(blank=True, null=True)  

    #Relacion a la actividad
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        related_name='actividad_informes_de_actividad_principal',
        null=True,
        blank=True
    )

    #Usuario que genera el informe de actividad
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='informe_actividad_creados_usuario',
        null=True,
        blank=True
    )

    #Generar el numero de informe
    def generar_numero_informe(self):
        """
        Generar numero de informes de actividad automatico:
        INFACT-ID-CODIGO_ACTIVIDAD
        """
        if not self.actividad or not self.actividad.codigo:
            raise ValueError("La actividad debe tener un código para generar el número de informe")
        
        # Si ya tiene ID, formatear con 4 dígitos
        if self.id:
            id_formateado = f"{self.id:04d}"
            return f"INFACT-{id_formateado}-{self.actividad.codigo}"
        else:
            # Si no tiene ID, usar placeholder
            return f"INFACT-{{id:04d}}-{self.actividad.codigo}"
    
    #Metodo guardado
    def save(self, *args, **kwargs):
        # Guardar primero si no tiene ID
        is_new = self.pk is None
        
        if is_new:
            # Guardar para obtener ID
            super().save(*args, **kwargs)
            
            # Generar número con ID formateado
            if self.actividad and self.actividad.codigo:
                id_formateado = f"{self.id:04d}"
                self.numeroInforme = f"INFACT-{id_formateado}-{self.actividad.codigo}"
                # Actualizar sin recursión
                InformeActividadPrincipal.objects.filter(pk=self.pk).update(numeroInforme=self.numeroInforme)
        else:
            # Si ya existe, solo actualizar si no tiene número
            if not self.numeroInforme and self.actividad:
                id_formateado = f"{self.id:04d}"
                self.numeroInforme = f"INFACT-{id_formateado}-{self.actividad.codigo}"
            
            super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Informe de Actividad Principal'
        verbose_name_plural = 'Informes de Actividades Principal'

    #metodo str                
    def __str__(self):
        return f"Informe {self.numeroInforme} - {self.actividad.codigo if self.actividad else 'Sin actividad'}"    


#Informe de subactividad Principal
class InformeTareaPrincipal(InformeActividadBase):
    objetivoTarea = models.TextField(blank=True, null=True)
    informeObjetivoTarea = models.TextField(blank=True, null=True)
    tipoActividad = models.CharField(max_length=255, blank=True, null=True)
    desglosePresupuesto = models.JSONField(blank=True, null=True)

    #Tarea relacionada al Informe de tarea
    tarea = models.ForeignKey(
        TareaActividad,
        on_delete=models.SET_NULL,
        related_name='tarea_informes_de_subactividad_principal',
        null=True,
        blank=True
    )

    #Usuario que genero el informe
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='informes_tarea_creados_usuario',
        null=True,
        blank=True,
    )

    #generar el numero de informe para tareas
    def generar_numero_informe(self):
        """
        Generar numero de informe de tarea automatico:
        INFSUBACT-ID_FORMATEADO-CODIGO_TAREA
        """
        if not self.tarea or not self.tarea.codigo:
            raise ValueError("La tarea debe tener un código para generar el número de informe")
        
        # Si ya tiene ID, formatear 4 dígitos
        if self.id:
            id_formateado = f"{self.id:04d}"
            return f"INFSUBACT-{id_formateado}-{self.tarea.codigo}"
        else:
            # Si no tiene ID, usar placeholder
            return f"INFSUBACT-{{id:04d}}-{self.tarea.codigo}"
    
    #Metodo de guardado
    def save(self, *args, **kwargs):
        #guardar primero si no tiene ID
        is_new = self.pk is None

        if is_new:
            #guardar para obtener el ID
            super().save(*args, **kwargs)
            # Generar número con ID formateado
            if self.tarea and self.tarea.codigo:
                id_formateado = f"{self.id:04d}"
                self.numeroInforme = f"INFSUBACT-{id_formateado}-{self.tarea.codigo}"
                # Actualizar sin recursión
                InformeTareaPrincipal.objects.filter(pk=self.pk).update(numeroInforme=self.numeroInforme)
        else:    
            #Si ya existe, solo actualizar
            if not self.numeroInforme and self.tarea:
                id_formateado = f"{self.id:04d}"
                self.numeroInforme = f"INFSUBACT-{id_formateado}-{self.tarea.codigo}"
            
            super().save(*args, **kwargs)

#Informe Base
class InformeBase(PolymorphicModel):
    numeroInforme = models.CharField(max_length=50, blank=True, null=True)
    fecha_ejecucion = models.DateField(blank=True, null=True)
    contribucion_proyecto = models.JSONField(blank=True, null=True)
    avance_indicadores = models.JSONField(blank=True, null=True)
    informacion_cuantitativa = models.TextField(blank=True, null=True)
    herramientas_evaluacion = models.TextField(blank=True, null=True)
    medios_verificacion = models.TextField(blank=True, null=True)
    comentarios_recomendaciones = models.TextField(blank=True, null=True)
    presupuesto_planificado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Presupuesto planificado', blank=True, null=True)
    presupuesto_ejecutado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Presupuesto ejecutado', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Informe Base actividada y subactividad'
        verbose_name_plural = 'Informes Base actividad y subactividad'

#Informe de actividad
class InfActividad(InformeBase):
    objetivo_actividad = models.TextField(blank=True, null=True)
    informe_objetivo_actividad = models.TextField(blank=True, null=True)
    tipo_actividad = models.CharField(max_length=255, blank=True, null=True)
    reporte_tipo = models.TextField(blank=True, null=True)
    procedencia_fondos = models.JSONField(blank=True, null=True)
    observaciones_presupuesto = models.TextField(blank=True, null=True)  
    archivos_cuantitativos = models.JSONField(blank=True, null=True)  
    herramientas_archivos = models.JSONField(blank=True, null=True)  
    medios_archivos = models.JSONField(blank=True, null=True)  

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        related_name='actividad_informes_de_actividad',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Informe de Actividad'
        verbose_name_plural = 'Informes de actividades'

    def __str__(self):
        return f"Informe {self.numeroInforme} - {self.actividad.codigo if self.actividad else 'Sin actividad'}"    


#Informe de tarea
class InfTarea(InformeBase):
    objetivo_tarea = models.TextField(blank=True, null=True)
    informe_objetivo_tarea = models.TextField(blank=True, null=True)
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

    def __str__(self):
        return f"Informe {self.numeroInforme} - {self.tarea.codigo if self.tarea else 'Sin Tarea'}"    


###################################Formularios actividades PEI####################
#Formulario de solicitud de fondos
class SolicitudFondosActPei(models.Model):
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='Detalle destino de fondos', blank=True, null=True)
    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitudes_fondo_pei',
        verbose_name='Forma de Pago',
        null=True,
        blank=True,
    )
    lugarSolicitud = models.TextField(blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='Fecha de la solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Monto Solicitado', blank=True, null=True)
    #Actividad
    fechaRealizacionActividad = models.DateField(verbose_name="Fecha de realizacion del actividad", blank=True, null=True)

    descripcion_actividad = models.TextField(verbose_name='Descripción de la actividad', blank=True, null=True)
    objetivo_actividad = models.TextField(verbose_name='Objetivo de la actividad', blank=True, null=True)
    datos_forma_pago = models.JSONField(verbose_name='Datos de forma de pago', blank=True, null=True)
    #Discriminador
    bloquearIconosSolFondos = models.BooleanField(default=True)
    #Validacion
    validacionResponsable = models.BooleanField(default=False)
    contador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_contador_solicitud_pei',
        null=True,
        blank=True,
    )
    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_solicitud_pei',
        null=True,
        blank=True,
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_solicitud_pei',
        null=True,
        blank=True,
    )
    actividad = models.ForeignKey(
        ActividadPei, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_pei_solicitud',
        null=True,
        blank=True,
    )

    tarea = models.ForeignKey(
        TareaActividadPei,
        on_delete=models.SET_NULL,
        related_name='tarea_pei_solicitud',
        null=True,
        blank=True,
    )

    # Campos automáticos de Django (si usas auto_now_add y auto_now)
    # created_at = models.DateTimeField(auto_now_add=True)  # Si existe
    # updated_at = models.DateTimeField(auto_now=True)      # Si existe

    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Fondos Actividad Pei'
        verbose_name_plural = 'Solicitudes de Fondos Actividad Pei'

    def save(self, *args, **kwargs):
        # Normalizar codigo vacío a None
        if self.numeroFormulario == '':
            self.numeroFormulario = None
        
        # Si es una nueva solicitud sin código, guardar primero para obtener el ID
        is_new = not self.pk
        needs_codigo = not self.numeroFormulario and self.actividad
        
        # Guardar para obtener el ID si es necesario
        super().save(*args, **kwargs)
        
        # Generar código usando el ID único de la tarea
        if is_new and needs_codigo:
            numero_formateado = f"{self.pk:04d}"
            #self.numeroFormulario = f"SACT-{numero_formateado}/{self.actividad.codigo}"
            self.numeroFormulario = f"{self.actividad.codigo}- SF{numero_formateado}"
            # Guardar nuevamente con el código generado
            super().save(update_fields=['numeroFormulario'])
        


#Solicitud de reembolso
class SolicitudReembolsoActPei(models.Model):
    #Datos del formulario
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='Detalle destino de fondos', blank=True, null=True)
    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitud_reembolso_pei',
        blank=True,
        null=True,
    )
    lugarSolicitud = models.CharField(max_length=50, verbose_name='Lugar solicitud', blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='Fecha solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Monto solicitado', blank=True, null=True)
    descripcion_actividad = models.TextField(blank=True, null=True, verbose_name='Descripción de la actividad')
    objetivo_actividad = models.TextField(blank=True, null=True, verbose_name='Objetivo de la actividad')
    datos_forma_pago = models.JSONField(blank=True, null=True, verbose_name='Datos de forma de pago')
    fechaRealizacionActividad = models.DateField(blank=True, null=True, verbose_name='Fecha de realizacion del actividad')

    #Bloquear iconos
    bloquearIconos = models.BooleanField(default=True)
        
    #Validaciones
    # validacionContador = models.BooleanField(default=False)
    # contador = models.ForeignKey(
    #     Usuario,
    #     on_delete=models.SET_NULL,
    #     related_name='usuario_contador_reembolso',
    #     null=True,
    #     blank=True,
    # )

    validacionResponsable = models.BooleanField(default=False)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_responsable_reembolso_pei',
        null=True,
        blank=True,
    )

    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_reembolso_pei',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_reembolso_pei',
        null=True,
        blank=True,
    )

    actividad = models.ForeignKey(
        ActividadPei, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_pei_reembolso',
        null=True,
        blank=True,
    )

    tarea = models.ForeignKey(
        TareaActividadPei,
        on_delete=models.SET_NULL,
        related_name='tarea_pei_reembolso',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Reembolso Act Pei'
        verbose_name_plural = 'Solicitudes de Reembolso Act Pei'

    def save(self, *args, **kwargs):
        if self.numeroFormulario == '':
            self.numeroFormulario = None
        
        is_new = not self.pk
        needs_codigo = not self.numeroFormulario and self.actividad
        
        super().save(*args, **kwargs)
        
        if is_new and needs_codigo:
            numero_formateado = f"{self.pk:04d}"
            self.numeroFormulario = f"{self.actividad.codigo} - SRPEI {numero_formateado}"
            super().save(update_fields=['numeroFormulario'])
        

#Solicitud de viaje
class SolicitudViajeActPei(models.Model):
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
        related_name='solicitud_viaje_fondo_pei',
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
        related_name='usuario_responsable_sol_viaje_pei',
        null=True,
        blank=True,
    )

    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_sol_viaje_pei',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_sol_viaje_pei',
        null=True,
        blank=True,
    )

    actividad = models.ForeignKey(
        ActividadPei, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_sol_viaje_pei',
        null=True,
        blank=True,
    )

    tarea = models.ForeignKey(
        TareaActividadPei,
        on_delete=models.SET_NULL,
        related_name='tarea_solicitud_sol_viaje_pei',
        null=True,
        blank=True,
    )
    
    datos_forma_pago = models.JSONField(
        verbose_name='Datos de forma de pago', 
        blank=True, 
        null=True,
        help_text='Información de forma de pago (transferencia, otros, etc.)'
    ) 
    
    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Viaje Actividad Pei'
        verbose_name_plural = 'Solicitudes de Viaje Actividad Pei'
    
    def save(self, *args, **kwargs):
        # Normalizar codigo vacío a None
        if self.numeroFormulario == '':
            self.numeroFormulario = None
        
        # Si es una nueva solicitud sin código, guardar primero para obtener el ID
        is_new = not self.pk
        needs_codigo = not self.numeroFormulario and self.actividad
        
        # Guardar para obtener el ID si es necesario
        super().save(*args, **kwargs)
        
        # Generar código usando el ID único de la tarea
        if is_new and needs_codigo:
            numero_formateado = f"{self.pk:04d}"
            #self.numeroFormulario = f"SACT-{numero_formateado}/{self.actividad.codigo}"
            self.numeroFormulario = f"{self.actividad.codigo}-SV{numero_formateado}"
            # Guardar nuevamente con el código generado
            super().save(update_fields=['numeroFormulario'])
        


class SolicitudPagoDirectoActPei(models.Model):
    numeroFormulario = models.CharField(max_length=150, blank=True, null=True)
    detalleDestinoFondos = models.JSONField(verbose_name='detalle_destino_fondos', blank=True, null=True)
    formaPago = models.ForeignKey(
        FormaPago,
        on_delete=models.SET_NULL,
        related_name='solicitud_pago_directo_pei',
        null=True,
        blank=True,
    )
    lugarSolicitud = models.TextField(blank=True, null=True)
    fechaSolicitud = models.DateField(verbose_name='fecha_solicitud', blank=True, null=True)
    montoSolicitado = models.DecimalField(max_digits=6,decimal_places=2,verbose_name ='monto_solicitado',blank=True, null=True)
    #Actividad
    fechaRealizacionActividad = models.DateField(verbose_name="Fecha de realizacion del actividad", blank=True, null=True)

    descripcion_actividad = models.TextField(blank=True, null=True, verbose_name='Descripción de la actividad')
    objetivo_actividad = models.TextField(blank=True, null=True, verbose_name='Objetivo de la actividad')
    datos_forma_pago = models.JSONField(verbose_name='Datos de forma de pago', blank=True, null=True)
    
    #Discriminador
    bloquearIconosSolFondos = models.BooleanField(default=True)
    
     #Validaciones
    validacionResponsable = models.BooleanField(default=False)
    contador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_contador_sol_pago_directo_pei',
        null=True,
        blank=True,
    )

    validacionCoordinador = models.BooleanField(default=False)
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_sol_pago_directo_pei',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_sol_pago_directo_pei',
        null=True,
        blank=True,
    )

    actividad = models.ForeignKey(
        ActividadPei, 
        on_delete=models.SET_NULL,
        related_name='usuario_actividad_sol_pago_directo_pei',
        null=True,
        blank=True,
    ) 

    tarea = models.ForeignKey(
        TareaActividadPei,
        on_delete=models.SET_NULL,
        related_name='tarea_solicitud_sol_pago_directo_pei',
        null=True,
        blank=True,
    )  
    
    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Solicitud de Pago Directo Act Pei'
        verbose_name_plural = 'Solicitudes de Pago Directo Act Pei'

    def save(self, *args, **kwargs):
        # Normalizar codigo vacío a None
        if self.numeroFormulario == '':
            self.numeroFormulario = None
        
        # Si es una nueva solicitud sin código, guardar primero para obtener el ID
        is_new = not self.pk
        needs_codigo = not self.numeroFormulario and self.actividad
        
        # Guardar para obtener el ID si es necesario
        super().save(*args, **kwargs)
        
        # Generar código usando el ID único de la tarea
        if is_new and needs_codigo:
            numero_formateado = f"{self.pk:04d}"
            #self.numeroFormulario = f"SACT-{numero_formateado}/{self.actividad.codigo}"
            self.numeroFormulario = f"{self.actividad.codigo}-SPDPEI{numero_formateado}"
            # Guardar nuevamente con el código generado
            super().save(update_fields=['numeroFormulario'])
        


#Rendicion de cuentas
class RendicionCuentasActPei(models.Model):
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
        ActividadPei,
        on_delete=models.SET_NULL,
        related_name='rendicion_cuentas_actividad_pei',
        null=True,
        blank=True,
    )
    fechaActividad = models.DateField(verbose_name='Fecha de la actividad', blank=True, null=True)
    fechaRendicion = models.DateField(verbose_name='Fecha de Rendición', auto_now_add=True, blank=True, null=True)
    descripcionActividad = models.TextField(blank=True, null=True)
    lugarActividad = models.TextField(blank=True, null=True)
    lugarRendicion = models.TextField(blank=True, null=True)
    tarea = models.ForeignKey(
        TareaActividadPei,
        on_delete=models.SET_NULL,
        related_name='rendicion_cuentas_tarea_actividad_pei',
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
        related_name='usuario_responsable_rendicion_pei',
        null=True,
        blank=True,
    )
    validacionCoordinador = models.BooleanField(default=False)    
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_coordinador_rendicion_pei',
        null=True,
        blank=True,
    )

    validacionContador = models.BooleanField(default=False)
    contador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_contador_rendicion_pei',
        null=True,
        blank=True,
    )

    validacionAdministrador = models.BooleanField(default=False)
    administrador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_administrador_rendicion_pei',
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='usuario_rendicion_pei',
        null=True,
        blank=True,
    )
    #Solicitud
    solicitudFondos = models.ForeignKey(
        SolicitudFondosActPei,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_fondos_pei',
        null=True,
        blank=True,
    )
    solicitudReembolso = models.ForeignKey(
        SolicitudReembolsoActPei,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_reembolso_pei',
        null=True,
        blank=True,
    )
    solicitudViaje = models.ForeignKey(
        SolicitudViajeActPei,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_viaje_pei',
        null=True,
        blank=True,
    )
    solicitudPagoDirecto = models.ForeignKey(
        SolicitudPagoDirectoActPei,
        on_delete=models.SET_NULL,
        related_name='rendicion_sol_pago_directo_pei',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.numeroFormulario}"

    class Meta:
        verbose_name = 'Rendicion de cuentas Actividad PEI'
        verbose_name_plural = 'Rendiciones de cuentas Actividad PEI'

    def save(self, *args, **kwargs):
        if self.numeroFormulario == '':
            self.numeroFormulario = None
        
        is_new = not self.pk
        needs_codigo = not self.numeroFormulario and self.actividad
        
        super().save(*args, **kwargs)
        
        if is_new and needs_codigo:
            numero_formateado = f"{self.pk:04d}"
            self.numeroFormulario = f"{self.actividad.codigo} - RCPEI {numero_formateado}"
            super().save(update_fields=['numeroFormulario'])


#Inoforme de Actividad Pei Principal 
class InformeActividadPrincipalPei(InformeActividadBase):
    objetivoActividad = models.TextField(blank=True, null=True)
    informeObjetivoActividad = models.TextField(blank=True, null=True)
    tipoActividad = models.CharField(max_length=255, blank=True, null=True)
    reporteTipo = models.TextField(blank=True, null=True)
    procedenciaFondos = models.JSONField(blank=True, null=True)
    observacionesPresupuesto = models.TextField(blank=True, null=True)  
    archivosCuantitativos = models.JSONField(blank=True, null=True)  
    herramientasArchivos = models.JSONField(blank=True, null=True)  
    mediosArchivos = models.JSONField(blank=True, null=True)  

    #Relacion a la actividad
    actividad = models.ForeignKey(
        ActividadPei,
        on_delete=models.SET_NULL,
        related_name='actividad_informes_de_actividad_principal_pei',
        null=True,
        blank=True
    )

    #Usuario que genera el informe de actividad
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='informe_actividad_pei_creados_usuario',
        null=True,
        blank=True
    )

    # #Generar el numero de informe
    # def generar_numero_informe(self):
    #     """
    #     Generar numero de informes de actividad automatico:
    #     INFACT-ID-CODIGO_ACTIVIDAD
    #     """
    #     if not self.actividad or not self.actividad.codigo:
    #         raise ValueError("La actividad debe tener un código para generar el número de informe")
        
    #     # Si ya tiene ID, formatear con 4 dígitos
    #     if self.id:
    #         id_formateado = f"{self.id:04d}"
    #         return f"INFACT-{id_formateado}-{self.actividad.codigo}"
    #     else:
    #         # Si no tiene ID, usar placeholder
    #         return f"INFACT-{{id:04d}}-{self.actividad.codigo}"
    
    # #Metodo guardado
    # def save(self, *args, **kwargs):
    #     # Guardar primero si no tiene ID
    #     is_new = self.pk is None
        
    #     if is_new:
    #         # Guardar para obtener ID
    #         super().save(*args, **kwargs)
            
    #         # Generar número con ID formateado
    #         if self.actividad and self.actividad.codigo:
    #             id_formateado = f"{self.id:04d}"
    #             self.numeroInforme = f"INFACT-{id_formateado}-{self.actividad.codigo}"
    #             # Actualizar sin recursión
    #             InformeActividadPrincipal.objects.filter(pk=self.pk).update(numeroInforme=self.numeroInforme)
    #     else:
    #         # Si ya existe, solo actualizar si no tiene número
    #         if not self.numeroInforme and self.actividad:
    #             id_formateado = f"{self.id:04d}"
    #             self.numeroInforme = f"INFACT-{id_formateado}-{self.actividad.codigo}"
            
    #         super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Informe de Actividad PEI Principal'
        verbose_name_plural = 'Informes de Actividades PEI Principal'

    #metodo str                
    def __str__(self):
        return f"Informe {self.numeroInforme} - {self.actividad.codigo if self.actividad else 'Sin actividad'}"    


#Informe de subactividad/Tarea PEI Principal
class InformeTareaPrincipalPei(InformeActividadBase):
    objetivoTarea = models.TextField(blank=True, null=True)
    informeObjetivoTarea = models.TextField(blank=True, null=True)
    tipoActividad = models.CharField(max_length=255, blank=True, null=True)
    desglosePresupuesto = models.JSONField(blank=True, null=True)

    #Tarea relacionada al Informe de tarea
    tarea = models.ForeignKey(
        TareaActividadPei,
        on_delete=models.SET_NULL,
        related_name='tarea_pei_informes_de_subactividad_principal',
        null=True,
        blank=True
    )

    #Usuario que genero el informe
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='informes_tarea_pei_creados_usuario',
        null=True,
        blank=True,
    )

    #generar el numero de informe para tareas
    # def generar_numero_informe(self):
    #     """
    #     Generar numero de informe de tarea automatico:
    #     INFSUBACT-ID_FORMATEADO-CODIGO_TAREA
    #     """
    #     if not self.tarea or not self.tarea.codigo:
    #         raise ValueError("La tarea debe tener un código para generar el número de informe")
        
    #     # Si ya tiene ID, formatear 4 dígitos
    #     if self.id:
    #         id_formateado = f"{self.id:04d}"
    #         return f"INFSUBACT-{id_formateado}-{self.tarea.codigo}"
    #     else:
    #         # Si no tiene ID, usar placeholder
    #         return f"INFSUBACT-{{id:04d}}-{self.tarea.codigo}"
    
    #Metodo de guardado
    # def save(self, *args, **kwargs):
    #     #guardar primero si no tiene ID
    #     is_new = self.pk is None

    #     if is_new:
    #         #guardar para obtener el ID
    #         super().save(*args, **kwargs)
    #         # Generar número con ID formateado
    #         if self.tarea and self.tarea.codigo:
    #             id_formateado = f"{self.id:04d}"
    #             self.numeroInforme = f"INFSUBACT-{id_formateado}-{self.tarea.codigo}"
    #             # Actualizar sin recursión
    #             InformeTareaPrincipal.objects.filter(pk=self.pk).update(numeroInforme=self.numeroInforme)
    #     else:    
    #         #Si ya existe, solo actualizar
    #         if not self.numeroInforme and self.tarea:
    #             id_formateado = f"{self.id:04d}"
    #             self.numeroInforme = f"INFSUBACT-{id_formateado}-{self.tarea.codigo}"
            
    #         super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Informe de Subactividad PEI Principal'
        verbose_name_plural = 'Informes de Subactividades PEI Principal'

    def __str__(self):
        return f"Informe {self.numeroInforme} - {self.tarea.codigo if self.tarea else 'Sin Tarea'}"    




#Importar los modelos para vinculaciones
from .modelos_vinculaciones import VinculacionSolicitudInforme