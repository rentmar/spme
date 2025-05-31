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
    codigo = models.CharField(max_length=50)
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



# Indicadores del PEI
class IndicadorPeiBase(PolymorphicModel):
    codigo = models.CharField(max_length=15)
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



    class Meta:
        verbose_name = 'Indicador PEI'
        verbose_name_plural = 'Indicadores PEI'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
    
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
    codigo = models.CharField(max_length=10)
    clasificador = models.CharField(max_length=5, null=True, blank=True)
    instancia = models.CharField(max_length=255)

    class Meta:
        ordering = ['-codigo']
        verbose_name = 'Instancia Gestora'
        verbose_name_plural = 'Instancias Gestoras'

    def __str__(self):
        return f"{self.codigo} - {self.instancia}"    


#Definicion de la clase Proyecto
class Proyecto(models.Model):
    ESTADO_OPCIONES = [
        ('ES','Estructuracion'),
        ('EP','En Planificacion'),
    ]
    #Informacion basica
    codigo = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)

    #Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_finalizacion = models.DateField(null=True, blank=True)

    #Presupuesto
    presupuesto = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)

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

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"



# Objetivo General DEL PROYECTO
class ObjetivoGeneralProyecto(models.Model):
    codigo = models.CharField(max_length=10, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    supuestos = models.TextField(blank=True)
    riesgos = models.TextField(blank=True)

    #Relaciones
    proyecto = models.OneToOneField(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='objetivo_general',
        verbose_name='Proyecto asociado'
    )
    
    class Meta:
        verbose_name = 'Objetivo General del Proyecto'
        verbose_name_plural = 'Objetivos Generales del Proyecto'
    
    def __str__(self):
        return f"OO-{self.proyecto.codigo}: {self.descripcion[:50]}..."

# KPI
class Kpi(models.Model):
    codigo = models.CharField(max_length=10, null=True, blank=True)
    descripcion = models.TextField(verbose_name="Redaccion del KPI")
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
    codigo = models.CharField(max_length=10)
    descripcion = models.TextField()
    supuestos = models.TextField(blank=True, null=True)
    riesgos = models.TextField(blank=True, null=True)
    
    #Relaciones
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='objetivos_especificos',
        verbose_name='Proyecto asociado',
    )
    
    class Meta:
        verbose_name = 'Objetivo Especifico del Proyecto'
        verbose_name_plural = 'Objetivos Especificos del Proyecto'

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:50]}..."    
    
#Procesos - Linea de Accion
class Proceso(models.Model):
    codigo = models.CharField(max_length=15)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'



# Resultado
class ResultadoProyecto(PolymorphicModel):
    codigo = models.CharField(max_length=10, blank=True, null=True)
    descripcion = models.TextField(blank=True)
    supuestos = models.TextField(blank=True)
    riesgos = models.TextField(blank=True)
    class Meta:
        verbose_name = 'Resultado de Proyecto'
        verbose_name_plural = 'Resultados de Proyecto'

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:30]}..."

#Resultado de Objetivo General
class ResultadoOG(ResultadoProyecto):
    proceso = models.OneToOneField(
        Proceso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultado_og'
    )
    class Meta:
        verbose_name = 'Resultado Objetivo General'
        verbose_name_plural = 'Resultados Objetivo General'

#Resultado de Objetivo Especifico
class ResultadoOE(ResultadoProyecto):
    proceso = models.OneToOneField(
        Proceso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultado_oe'
    )
    class Meta:
        verbose_name = 'Resultado Objetivo Especifico'
        verbose_name_plural = 'Resultados Objetivo Especifico'

# Producto
class ProductoProyecto(PolymorphicModel):
    codigo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True), 
    supuestos = models.TextField(blank=True, null=True)
    riesgos = models.TextField(blank=True, null=True)
    entregado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Producto del Proyecto'
        verbose_name_plural = 'Productos del Proyecto'

    def __str__(self):
        return {self.codigo} - self.descripcion[:50]    


#Producto Objetivo Especifico
class ProductoOE(ProductoProyecto):
    proceso = models.OneToOneField(
        Proceso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='producto_oe'
    )
    class Meta:
        verbose_name = 'Producto Objetivo Especifico'
        verbose_name_plural = 'Productos Objetivos Especificos'


#Producto de Resultado Objetivo Especifico
class ProductoResultadoOE(ProductoProyecto):
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
    codigo = models.CharField(max_length=20)
    redaccion = models.CharField(max_length=5, choices=TIPO_INDICADOR)
    fuente_verificacion = models.TextField()
    target_poblacion = models.CharField(max_length=255)
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
        related_name='indicador_res_og'
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

