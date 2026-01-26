from django.db import models
from spme_estructuracion_proyecto.models import InstanciaGestora, ProcedenciaFondos, IndicadorProyecto
from spme_estructuracion_pei.models import Pei
from spme_autenticacion.models import Usuario

#Modelo Departamento Bolivia

class DepartamentoBolivia(models.Model):
    codigo = models.CharField(max_length=5)
    nombre = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Departamento Bolivia"
        verbose_name_plural = "Departamentos Bolivia"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

#Modelo de la Institución
class Institucion(models.Model):
    sigla = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=500, blank=True, null=True)
    emailInstitucion = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    casillaPostal = models.CharField(max_length=150, blank=True, null=True)
    webSite = models.CharField(max_length=150, blank=True, null=True)

    #Relacion con los departamentos
    departamento = models.ManyToManyField(
        DepartamentoBolivia, 
        related_name='instituciones', 
        verbose_name='Departamentos de intervencion',
        blank=True,
    )
    
    class Meta:
        verbose_name = "Institución"
        verbose_name_plural = "Instituciones"
        ordering = ['nombre']
    
    def __str__(self):
        return self.sigla or self.nombre or f"Institución {self.id}"
    
    @property
    def total_proyectos(self):
        """Cantidad de proyectos de esta institución"""
        return self.proyectos.count()
    
    @property
    def proyectos_activos(self):
        """Proyectos activos de esta institución"""
        return self.proyectos.filter(estado='PL')  # Solo planificados como ejemplo


#Modelo del proyecto FONFOSC
class ProyectoFonFosc(models.Model):
    ESTADO_OPCIONES = [
        ('ES','Estructuracion'),
        ('PL','Planificado'),
        ('OBS','Observado'),
        ('APROB','Aprobado'),
        ('EJ','En Ejecucion'),
        ('FIN','Finalizado'),
    ]

    CATEGORIA_PROYECTO = [
        ('FI','Fortalecimiento Institucional'),
        ('FSC','Fortalecimiento de la sociedad civil'),
    ]

    #Informacion basica
    codigo = models.CharField(max_length=50, unique=True)
    titulo = models.TextField(null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)

    #Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_finalizacion = models.DateField(null=True, blank=True)

    categoria = models.CharField(max_length=3, choices=CATEGORIA_PROYECTO, default='FI')
    cobertura_geografica = models.TextField(blank=True, null=True)

    #Presupuesto
    presupuesto = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)

    #Estados
    estado = models.CharField(max_length=10, choices=ESTADO_OPCIONES, default='ES')
    
    # RELACIÓN CON INSTITUCIÓN (Foreign Key - UNA institución tiene VARIOS proyectos)
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,  # O SET_NULL si quieres permitir que quede sin institución
        related_name='proyectos',  # ¡IMPORTANTE! institucion.proyectos.all()
        verbose_name='Institución responsable',
        help_text='Institución a la que pertenece este proyecto'
        # null=True,  # Descomenta si puede no tener institución
        # blank=True,  # Descomenta si puede no tener institución
    )
    
    #Responsable (persona)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proyectos_responsable',
        verbose_name='Responsable del proyecto'
    )

    #Relaciones
    pei = models.ForeignKey(
        Pei,
        on_delete=models.PROTECT,
        related_name='proyectos_fonfosc',
        verbose_name='PEI asociado',
    )

    procedencia_fondos = models.ManyToManyField(
        ProcedenciaFondos,
        related_name='proyectos_fonfosc',
        verbose_name='Financiador(es) proyecto',
        help_text='Financiador(es) del proyecto'
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        # Puedes agregar índices para mejor performance
        indexes = [
            models.Index(fields=['institucion', 'estado']),
            models.Index(fields=['codigo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"
    
    @property
    def institucion_info(self):
        """Información resumida de la institución"""
        if self.institucion:
            return f"{self.institucion.sigla or self.institucion.nombre}"
        return "Sin institución asignada"


#Objetivo del Proyecto
class ObjetivoFonfosc(models.Model):
    #Relacion a Proyecto
    proyecto = models.OneToOneField(
        ProyectoFonFosc,
        on_delete=models.CASCADE,
        related_name='objetivo_general_fonfosc',
        verbose_name='Proyecto asociado'
    )
    codigo = models.CharField(max_length=50)
    redaccion = models.TextField(blank=True, null=True)
    supuestosRiesgos = models.TextField(blank=True, null=True)



# Resultado
class ResultadoFonfosc(models.Model):
    codigo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True)
    supuestosRiesgos = models.TextField(blank=True)

    # RELACIÓN CON OBJETIVO - UN objetivo tiene VARIOS resultados
    objetivo = models.ForeignKey(
        ObjetivoFonfosc,
        on_delete=models.CASCADE,
        related_name='resultados_fonfosc',  # objetivo.resultados_fonfosc.all()
        verbose_name='Objetivo asociado'
    )
    
    class Meta:
        verbose_name = 'Resultado de Proyecto'
        verbose_name_plural = 'Resultados de Proyecto'

    def __str__(self):
        return f"{self.id}-{self.codigo} - {self.descripcion[:30]}..."
    
#Indicador Fonfosc
class IndicadorFonFosc(IndicadorProyecto):
    #RELACION DON RESULTADO 
    resultado = models.ForeignKey(
        ResultadoFonfosc,
        on_delete=models.CASCADE,
        related_name='indicador_resultado_fonfosc',  # objetivo.resultados_fonfosc.all()
        verbose_name='Indicador de Resultado',
    )

    class Meta:
        verbose_name = 'Indicador FonFosc'
        verbose_name_plural = 'Indicadores FonFosc'    

#Indicador de objetivo
class IndicadorObjetivoFonFosc(IndicadorProyecto):
    #RELACION DON RESULTADO 
    objetivo = models.ForeignKey(
        ObjetivoFonfosc,
        on_delete=models.CASCADE,
        related_name='indicador_objetivo_fonfosc',  
        verbose_name='Indicador de Objetivo FonFosc',
    )
    class Meta:
        verbose_name = 'Indicador de Objetivo Fonfosc'
        verbose_name_plural = 'Indicadores de Objetivo Fonfosc'


#Secciones
class Pertinencia(models.Model):
    ordinal = models.IntegerField(blank=True, null=True)