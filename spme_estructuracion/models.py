from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

####################### PEI ##########################################
class Pei(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(default=timezone.now, null=True, blank=True)
    fecha_fin = models.DateField(default=timezone.now, null=True, blank=True)
    esta_vigente = models.BooleanField(default=False)

    creado_el = models.DateTimeField(auto_now_add=True)
    modificado_el = models.DateTimeField(auto_now=True)

    class Meta:  
        verbose_name = 'PEI'
        verbose_name_plural = 'PEIs'
        ordering = ['titulo']  

    def __str__(self):
        return self.titulo



#ObjetivoGeneralPei
class ObjetivoPei(models.Model):
    codigo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField()
    pei = models.ForeignKey(
        Pei, 
        on_delete=models.CASCADE, 
        related_name='pei_obj_general')
    
    creado_el = models.DateTimeField(auto_now_add=True)
    modificado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Objetivo General PEI'
        verbose_name_plural = 'Objetivos Generales PEI'

    def __str__(self):
        return self.codigo


#Factores criticos
class FactoresCriticos(models.Model):
    factor_critico = models.TextField(null=True, blank=True)
    #Relaciones
    objetivo_especifico = models.ForeignKey(
        ObjetivoPei,
        on_delete=models.SET_NULL,
        related_name='factores_criticos',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Factor critico'
        verbose_name_plural = 'Factores criticos'

    def __str__(self):
        return self.factor_critico    




# Indicadores del PEI
class IndicadorPeiBase(PolymorphicModel):
    codigo = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(verbose_name='Indicador')
    captura_informacion = models.TextField(blank=True, null=True)
    responsabilidad = models.CharField(max_length=255, blank=True, null=True)
    frecuencia_recopilacion = models.CharField(max_length=255, blank=True, null=True)
    uso_informacion = models.TextField(blank=True, null=True)
    
    #Fechas
    creado_el = models.DateTimeField(auto_now_add=True)
    modificado_el = models.DateTimeField(auto_now=True)

    #Relacion al objetivo
    objetivo = models.ForeignKey(
        ObjetivoPei, 
        on_delete=models.CASCADE,
        related_name='indicador_pei_objetivo',
        null=True,
        blank=True
    )

    #Relacion al Pei
    """
    pei = models.ForeignKey(
        Pei,
        on_delete=models.CASCADE,
        related_name='indicador_pei_pei',
        null=True,
        blank=True,
    )
    """


    class Meta:
        verbose_name = 'Indicador PEI'
        verbose_name_plural = 'Indicadores PEI'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.id}, {self.codigo} - {self.descripcion}"
    
#Indicador Cuantitativo
class IndicadorPeiCuantitativo(IndicadorPeiBase):
    TIPO_MEDICION = 'Proporcion'
    #tipo del inidicador
    tipo = models.CharField(max_length=20, default=TIPO_MEDICION, editable=False, verbose_name='Tipo')        
    #Atributos de Proporcion
    numerador = models.TextField(blank=True, null=True)
    denominador = models.TextField(blank=True, null=True)
    umbral_des_numeral = models.IntegerField(blank=True, null=True)
    umbral_des_literal_um1 = models.TextField(blank=True, null=True)
    umbral_des_literal_um2 = models.TextField(blank=True, null=True)
    umbral_des_literal_um3 = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Indicador Cuantitativo PEI'
        verbose_name_plural = 'Indicadores Cuantitativos PEI'

#Indicador cualitativo, señal de avance
class IndicadorPeiCualitativo(IndicadorPeiBase):
    TIPO_MEDICION = 'Avance'

    #tipo del inidicador
    tipo = models.CharField(max_length=20, default=TIPO_MEDICION, editable=False, verbose_name='Tipo')        
    #Atributos de Proporcion
    umbral_des_literal_um1 = models.TextField(blank=True, null=True)
    umbral_des_literal_um2 = models.TextField(blank=True, null=True)
    umbral_des_literal_um3 = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Indicador Cualitativo PEI'
        verbose_name_plural = 'Indicadores Cualitativos PEI'


############### PROYECTOS #######################

#Definicion de la Instancia gestora.
class InstanciaGestora(models.Model):
    codigo = models.CharField(max_length=50, null=True, blank=True)
    clasificador = models.CharField(max_length=5, null=True, blank=True)
    instancia = models.CharField(max_length=255)

    class Meta:
        ordering = ['-codigo']
        verbose_name = 'Instancia Gestora'
        verbose_name_plural = 'Instancias Gestoras'

    def __str__(self):
        return f"{self.codigo} - {self.instancia}"    


#Registrar Procedencia de fondos
class ProcedenciaFondos(models.Model):
    sigla = models.CharField(max_length=15, null=True, blank=True)
    financiera = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Procedencia de Fondos'
        verbose_name_plural = 'Procedencia de Fondos'

    def __str__(self):
        return f"{self.sigla} - {self.financiera}"    

#Definicion de la clase Proyecto
class Proyecto(models.Model):
    ESTADO_OPCIONES = [
        ('ES','Estructuracion'),
        ('EP','En Planificacion'),
    ]

    #Informacion basica
    codigo = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=500)
    descripcion = models.TextField(blank=True, null=True)

    #Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_finalizacion = models.DateField(null=True, blank=True)

    #Presupuesto
    presupuesto = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)

    #Estados
    estado = models.CharField(max_length=2, choices=ESTADO_OPCIONES, default='ES')
    
    #Responsable
    instancia_gestora = models.ManyToManyField(InstanciaGestora, related_name='proyectos')
    creado_por = models.CharField(max_length=150, blank=True, null=True)

    #Relaciones
    pei = models.ForeignKey(
        Pei,
        on_delete=models.PROTECT,
        related_name='proyectos', #Nombre para la relacion inversa
        verbose_name='PEI asociado',
    )

    procedencia_fondos = models.ManyToManyField(
        ProcedenciaFondos,
        blank=True,
        related_name='procedencia_fondos',
        verbose_name='Financiador(es) proyecto',
        help_text='Financiador(es) del proyecto'
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"



# Objetivo General DEL PROYECTO
class ObjetivoGeneralProyecto(models.Model):
    codigo = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    supuestos = models.TextField(null=True, blank=True)
    riesgos = models.TextField(null=True, blank=True)

    #Relaciones
    proyecto = models.OneToOneField(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='objetivo_general',
        verbose_name='Proyecto asociado',
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = 'Objetivo General del Proyecto'
        verbose_name_plural = 'Objetivos Generales del Proyecto'
    
    def __str__(self):
        return f"OO-{self.proyecto.codigo}: {self.descripcion[:50]}..."

# KPI
class Kpi(models.Model):
    codigo = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(verbose_name="Redaccion del KPI", null=True, blank=True)
    #Relaciones
    objetivo_general = models.ForeignKey(
        ObjetivoGeneralProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpis',
        verbose_name='Objetivo General Asociado'
    )


# Objetivo Específico DEL PROYECTO
class ObjetivoEspecificoProyecto(models.Model):
    codigo = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    supuestos = models.TextField(blank=True, null=True)
    riesgos = models.TextField(blank=True, null=True)
    
    #Relaciones
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='objetivos_especificos',
        verbose_name='Proyecto asociado',
        help_text='Proyecto al que contribuye este objetivo especifico'
        
    )

    objetivo_general = models.ForeignKey(
        ObjetivoGeneralProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='objetivos_especificos_og',
        verbose_name='Objetivo general asociado',
        help_text='Objetivo general al que contribuye este objetivo especifico'
    )
    
    class Meta:
        verbose_name = 'Objetivo Especifico del Proyecto'
        verbose_name_plural = 'Objetivos Especificos del Proyecto'

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:50]}..."    



# Resultado
class ResultadoProyecto(PolymorphicModel):
    codigo = models.CharField(max_length=20, blank=True, null=True)
    descripcion = models.TextField(blank=True)
    supuestos = models.TextField(blank=True)
    riesgos = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Resultado de Proyecto'
        verbose_name_plural = 'Resultados de Proyecto'

    def __str__(self):
        return f"{self.id}-{self.codigo} - {self.descripcion[:30]}..."

#Resultado de Objetivo General
class ResultadoOG(ResultadoProyecto):
    #Relaciones
    objetivo_general = models.ForeignKey(
        ObjetivoGeneralProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultados_og',
        verbose_name='Objetivo General Asociado',
        help_text='Objetivo General al que contribuye este resultado'
    )
    class Meta:
        verbose_name = 'Resultado Objetivo General'
        verbose_name_plural = 'Resultados Objetivo General'

#Resultado de Objetivo Especifico
class ResultadoOE(ResultadoProyecto):
    objetivo_especifico = models.ForeignKey(
        ObjetivoEspecificoProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultados_oe',
        verbose_name='Objetivo Específico Asociado',
        help_text='Objetivo específico al que están relacionados estos resultados'
    )
    class Meta:
        verbose_name = 'Resultado Objetivo Especifico'
        verbose_name_plural = 'Resultados Objetivo Especifico'

# Producto
class ProductoProyecto(PolymorphicModel):
    codigo = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True), 
    supuestos = models.TextField(blank=True, null=True)
    riesgos = models.TextField(blank=True, null=True)
    entregado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Producto del Proyecto'
        verbose_name_plural = 'Productos del Proyecto'

    def __str__(self):
        return f"{self.codigo}"


#Producto Objetivo Especifico
class ProductoOE(ProductoProyecto):
    objetivo_especifico = models.ForeignKey(
        ObjetivoEspecificoProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_oe',
        verbose_name='Objetivo Especifico Asociado',
        help_text='Producto Esperado del Objetivo Especifico'
    )
    class Meta:
        verbose_name = 'Producto Objetivo Especifico'
        verbose_name_plural = 'Productos Objetivos Especificos'


#Producto de Resultado Objetivo Especifico
class ProductoResultadoOE(ProductoProyecto):
    #relaciones
    resultado_oe = models.ForeignKey(
        ResultadoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_res_oe',
        verbose_name='Producto del ResultadoOE Asociado',
        help_text='Producto Esperado del Resultado OE'

    )

    class Meta:
        verbose_name = 'Producto del Resultado Objetivo Especifico'
        verbose_name_plural = 'Productos del Resultado Objetivo Especifico'

    
#Indicadores
class IndicadorProyecto(PolymorphicModel):
    TIPO_INDICADOR = [
        ('GUIA', 'Indicador GUIA'),
        ('SMART', 'Indicador SMART'),
    ]

    TIPO = [
        ('A-Z', 'Literal'),
        ('1-9', 'Numerico'),
        ('%', 'Porcentual')
    ]

    # Campos comunes a todos los indicadores
    codigo = models.CharField(max_length=50, null=True, blank=True)
    redaccion = models.CharField(max_length=5, choices=TIPO_INDICADOR, blank=True, null=True)
    fuente_verificacion = models.TextField(blank=True, null=True)
    target_poblacion = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=5, choices=TIPO, default='A-Z')

    #Campos
    baseline = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
    )
    target_q1 = models.CharField(
        max_length=10,
        blank=True, 
        null=True,
    )
    target_q2 = models.CharField(
        max_length=10,
        blank=True, 
        null=True,
    )
    target_q3 = models.CharField(
        max_length=10,
        blank=True, 
        null=True,
    )
    target_q4 = models.CharField(
        max_length=10,
        blank=True, 
        null=True,
    )

    class Meta:
        verbose_name = 'Indicador de Proyecto'
        verbose_name_plural = 'Indicadores de Proyecto'

    def __str__(self):
        return f"{self.codigo} - {self.tipo}"

#Indicador de Objetivo General
class IndicadorObjetivoGeneral(IndicadorProyecto):
    objetivo_general = models.ForeignKey(
        ObjetivoGeneralProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='indicador_og'
    )
    class Meta:
        verbose_name = 'Indicador Objetivo General de Proyecto'
        verbose_name_plural = 'Indicadores Objetivo General de Proyecto'

#Indicador de Resultado de Objetivo General
class IndicadorResultadoObjGral(IndicadorProyecto):
    resultado_og = models.ForeignKey(
        ResultadoOG,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='indicador_res_og',
        verbose_name='Resultado de Objetivo General Asociado',
        help_text='Indicador que mide al Resultado de OG',
    )
    class Meta:
        verbose_name = 'Indicador Resultado Objetivo General de Proyecto'
        verbose_name_plural = 'Indicadores Resultado Objetivo General de Proyecto'

#Indicador de Objetivo Especifico
class IndicadorObjetivoEspecifico(IndicadorProyecto):
    objetivo_especifico = models.ForeignKey(
        ObjetivoEspecificoProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='indicador_oe'
    )
    class Meta:
        verbose_name = 'Indicador Objetivo Especifico de Proyecto'
        verbose_name_plural = 'Indicadores Resultado Objetivo General de Proyecto'

#Indicador Resultado de Objetivo Especifico
class IndicadorResultadoObjEspecifico(IndicadorProyecto):
    resultado_obj_especifico = models.ForeignKey(
        ResultadoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='indicador_res_oe'
    )
    class Meta:
        verbose_name = 'Indicador Resultado de Objetivo Especifico'
        verbose_name_plural = 'Indicadores Resultado Objetivo Especifico'



#Almacenamiento de Diagrama de estructura
class DiagramaEstructura(models.Model):
    codigoProyecto = models.CharField(max_length=50)
    nodos = models.JSONField(blank=True)
    conexiones = models.JSONField(blank=True)
    sincronizado = models.BooleanField(default=True)
    #Adicionales
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    #Relaciones
    proyecto = models.OneToOneField(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='mapa_nodo',
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = 'Diagrama Estructura'
        verbose_name_plural = 'Diagramas Estructura'

    def __str__(self):
        return f"Mapa: {self.codigoProyecto}"
    


#Procesos - Linea de Accion
class Proceso(models.Model):
    codigo = models.CharField(max_length=20, null=True, blank=True)
    titulo = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    #Relaciones
    resultado_og = models.ForeignKey(
        ResultadoOG,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proceso_resultado_og',
        verbose_name='Procesos asociados al Resultado del Objetivo General',
        help_text='Procesos que se ejecutan para alcanzar el Resultado OG'
    )

    resultado_oe = models.ForeignKey(
        ResultadoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proceso_resultado_oe',
        verbose_name='Procesos asociados al Resuldato del Objetivo Especifico',
        help_text='Procesos que se ejecutan para alcanzar el Resultado OE',
    )

    producto_oe = models.ForeignKey(
        ProductoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proceso_producto_oe',
        verbose_name='Procesos asociadoa al Producto del Objetivo Especifico',
        help_text='Procesos que se ejecutan para alcanzar el Producto OE',
    )


    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'

    def __str__(self):
        return f'Proceso: {self.titulo}'    

#Actividad
class Actividad(models.Model):
    ESTADOS_ACTIVIDAD = [
        ('SPLAN', 'Sin Planificar'),
        ('PLAN', 'Planificado'),
        ('EJEC', 'En Ejecución'),
        ('POST', 'Postergado'),
        ('CANC', 'Cancelado'),
        ('COMP', 'Completado'),
    ]
    PROCEDENCIA_FONDOS = [
        ('UG', 'Fondos de la Institucion'),
        ('PROY', 'Fondos del proyecto'),
    ]
    TIPO_ACTIVIDAD = [
        ('NODEF', 'No definido'),
        ('ACAP', 'Actividad de Capacitacion'),
        ('PRIN', 'Proyecto de Investigacion'),
        ('AOP', 'Actividad Operativa'),
        ('CSNS', 'Campaña de Sensibilizacion'),
        ('PDES', 'Proyecto de Desarrollo'),
        ('AINC', 'Actividad de Incidencia'),
        ('AART', 'Actividad de Articulacion'),
    ]
    codigo = models.CharField(max_length=20, blank=True, null=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPO_ACTIVIDAD, default='NODEF')
    fecha_programada = models.DateField(null=True, blank=True)
    duracion = models.IntegerField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    #Presupuesto
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    #Forndo de PEI
    presupuesto_pei = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    #Estado de la actividad
    estado = models.CharField(max_length=15, choices=ESTADOS_ACTIVIDAD, default='SPLAN')

    #Seleccion
    #- UG
    #- Fondos del Proyecto
    procedencia_fondos = models.CharField(max_length=25, choices=PROCEDENCIA_FONDOS, default='PROY')

    #Nuevos Campos
    objetivo_de_actividad = models.TextField(null=True, blank=True) #Nuevo datos
    descripcion_evaluacion = models.TextField(null=True, blank=True) #Toda la informacion de la planificacion de la actividad
    justificacion_modificacion = models.TextField(null=True, blank=True) #Motivos de modificacion 
    
    #Datos de la actividad segun su tipo
    datos_actividad = models.JSONField(null=True, blank=True)

    #Relaciones
    proceso = models.ForeignKey(
        Proceso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_proceso',
        verbose_name='Actividades relacionadas al Proceso',
        help_text='Actividades que se realizan para completar un proceso'
    )

    resultado_og = models.ForeignKey(
        ResultadoOG,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_resultado_og',
        verbose_name='Actividades relacionadas al Resultado OG',
        help_text='Actividades realizadas para completar el Resultado OG'
    )

    resultado_oe = models.ForeignKey(
        ResultadoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_resultado_oe',
        verbose_name='Actividades relacionadas al Resultado OE',
        help_text='Actividades realizadas para completar el Resultado OE',
    )

    producto_oe = models.ForeignKey(
        ProductoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_producto_oe',
        verbose_name='Actividades relacionadas al Producto OE',
        help_text='Actividades realizadas para completar el Producto OE',
    )

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f'Actividad: {self.codigo}'    


#PRoducto vinculado a todos los nodos
class ProductoGeneral(ProductoProyecto):
    #relaciones
    objetivo_general = models.ForeignKey(
        ObjetivoGeneralProyecto, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_generales_og',
        verbose_name='Producto general asociado a Objetivo General',
        help_text='Producto que puede asociarse a todos los nodos',
    )
    objetivo_especifico = models.ForeignKey(
        ObjetivoEspecificoProyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, 
        related_name='productos_generales_oe',
        verbose_name='Producto general asociado a objetivo especifico',
        help_text='Producto que puede asociarse a todos los nodos',
    )

    indicador_og = models.ForeignKey(
        IndicadorObjetivoGeneral,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_gral_indicador_og',
        verbose_name='Producto gral asociado al indicador OG',
        help_text='Producto que puede asociarse a todos los nodos',
    )

    indicador_oe = models.ForeignKey(
        IndicadorObjetivoEspecifico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_gral_indicador_oe',
        verbose_name='Producto gral asociado al indicador OE',
        help_text='Producto que puede asociarse a todos los nodos',
    )

    resultado_og = models.ForeignKey(
        ResultadoOG,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_gral_resultado_og',
        verbose_name='Producto gral asociado al Resultado OG',
        help_text='Producto que puede asociarse a todos los nodos',
    )

    resultado_oe = models.ForeignKey(
        ResultadoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_gral_resultado_oe',
        verbose_name='Producto gral asociado al Resultado OE',
        help_text='Producto que puede asociarse a todos los nodos',
    )

    indicador_resultado_og =models.ForeignKey(
        IndicadorResultadoObjGral,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_gral_indicador_resultado_og',
        verbose_name='Producto gral asociado al Indicador Resultado OG',
        help_text='Producto que puede asociarse a todos los nodos',
    )

    indicador_resultado_oe =models.ForeignKey(
        IndicadorResultadoObjEspecifico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_gral_indicador_resultado_oe',
        verbose_name='Producto gral asociado al Indicador Resultado OE',
        help_text='Producto que puede asociarse a todos los nodos',
    )



    #relaciones
    class Meta:
        verbose_name = 'Producto general (a toda la estructura)'
        verbose_name_plural = 'Productos generales (a toda la estructura)'




