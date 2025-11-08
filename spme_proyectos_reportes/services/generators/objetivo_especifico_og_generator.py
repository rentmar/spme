from django.http import HttpResponse
from ..base.base_report_service import BaseReportService
from spme_estructuracion_proyecto.models import (
    ObjetivoEspecificoProyecto,
    IndicadorObjetivoEspecifico,
    ResultadoOE,
    ProductoOE
)
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import InfActividad, InfTarea

class ObjetivoEspecificoOGGenerator(BaseReportService):
    def __init__(self):
        super().__init__()
    
    def generar_reporte_objetivo_especifico_og(self, objetivo_especifico_id, profundidad=1, incluir_detalles_actividades=True):
        """Genera reporte del objetivo específico con opción de encadenamiento y actividades"""
        try:
            objetivo_especifico = ObjetivoEspecificoProyecto.objects.select_related(
                'objetivo_general',
                'proyecto'
            ).prefetch_related(
                'indicador_oe',
                'resultados_oe',
                'productos_oe'
            ).get(id=objetivo_especifico_id)
            
            self._agregar_portada(objetivo_especifico)
            self._agregar_informacion_principal(objetivo_especifico)
            self._agregar_analisis_riesgos(objetivo_especifico)
            self._agregar_vinculaciones(objetivo_especifico)
            
            # ✅ ENCADENAR niveles inferiores según profundidad
            if profundidad > 1:
                self._agregar_indicadores_oe(objetivo_especifico)
            
            if profundidad > 1:
                self._agregar_resultados_oe(objetivo_especifico, profundidad)
            
            if profundidad > 1:
                self._agregar_productos_oe(objetivo_especifico, profundidad)
            
            # ✅ AGREGAR ACTIVIDADES VINCULADAS AL FINAL
            self._agregar_actividades_vinculadas(objetivo_especifico, incluir_detalles_actividades)
            
            return self._guardar_documento()
            
        except ObjetivoEspecificoProyecto.DoesNotExist:
            raise ValueError(f"Objetivo Específico con ID {objetivo_especifico_id} no encontrado")
    
    def _agregar_actividades_vinculadas(self, objetivo_especifico, incluir_detalles=True):
        """Agrega sección de actividades vinculadas a este objetivo específico"""
        actividades_vinculadas = self._obtener_actividades_por_objetivo_especifico(objetivo_especifico)
        
        if not actividades_vinculadas:
            self.document.add_heading('ACTIVIDADES VINCULADAS', level=1)
            p = self.document.add_paragraph()
            p.add_run("No hay actividades vinculadas directamente a este objetivo específico.").italic = True
            self.document.add_paragraph()
            return
        
        self.document.add_heading('ACTIVIDADES VINCULADAS AL OBJETIVO ESPECÍFICO', level=1)
        self.document.add_paragraph("Actividades que contribuyen al logro de este objetivo específico:")
        
        for actividad in actividades_vinculadas:
            self._agregar_actividad_completa(actividad, incluir_detalles)
    
    def _obtener_actividades_por_objetivo_especifico(self, objetivo_especifico):
        """Obtiene actividades vinculadas a este objetivo específico mediante estructuraProcedencia"""
        actividades_vinculadas = []
        
        # Obtener todas las actividades del proyecto
        if objetivo_especifico.proyecto:
            actividades_proyecto = Actividad.objects.filter(proyecto=objetivo_especifico.proyecto)
        else:
            return []
        
        # Filtrar actividades que referencian este objetivo específico
        for actividad in actividades_proyecto:
            if self._actividad_vincula_objetivo_especifico(actividad, objetivo_especifico.id):
                actividades_vinculadas.append(actividad)
        
        return actividades_vinculadas
    
    def _actividad_vincula_objetivo_especifico(self, actividad, objetivo_especifico_id):
        """Verifica si una actividad vincula este objetivo específico mediante estructuraProcedencia"""
        if not actividad.estructuraProcedencia:
            return False
        
        estructura = actividad.estructuraProcedencia
        datos_procedencia = estructura.get('datosProcedencia', {})
        
        # Verificar en objetivoespecificoog
        if 'objetivoespecificoog' in datos_procedencia:
            elemento = datos_procedencia['objetivoespecificoog']
            return self._elemento_coincide_id(elemento, objetivo_especifico_id)
        
        # Verificar en objetivoespecifico (para compatibilidad)
        if 'objetivoespecifico' in datos_procedencia:
            elemento = datos_procedencia['objetivoespecifico']
            return self._elemento_coincide_id(elemento, objetivo_especifico_id)
        
        return False
    
    def _elemento_coincide_id(self, elemento, id_buscado):
        """Verifica si un elemento de estructuraProcedencia coincide con el ID buscado"""
        if isinstance(elemento, dict):
            data = elemento.get('data', {})
            return data.get('id') == id_buscado
        elif isinstance(elemento, list):
            for elem in elemento:
                if isinstance(elem, dict):
                    data = elem.get('data', {})
                    if data.get('id') == id_buscado:
                        return True
        elif isinstance(elemento, str):
            return str(elemento) == str(id_buscado)
        return False
    
    def _agregar_actividad_completa(self, actividad, incluir_detalles=True):
        """Agrega una actividad completa con todas sus tareas e informes"""
        
        self.document.add_heading(f'📋 ACTIVIDAD: {actividad.codigo} - {actividad.nombreCorto}', level=2)
        
        # Información básica de la actividad
        self._agregar_info_basica_actividad(actividad)
        
        # Vinculaciones de la actividad
        if actividad.estructuraProcedencia:
            self._agregar_vinculaciones_actividad(actividad)
        
        # Tareas/Subactividades si se solicitan detalles
        if incluir_detalles:
            self._agregar_tareas_actividad(actividad)
        
        # Informes de la actividad si se solicitan detalles
        if incluir_detalles:
            self._agregar_informes_actividad(actividad)
        
        self.document.add_paragraph('=' * 80)
        self.document.add_paragraph()
    
    def _agregar_info_basica_actividad(self, actividad):
        """Agrega información básica de la actividad"""
        
        tabla_info = self.document.add_table(rows=8, cols=2)
        tabla_info.style = 'Light Grid Accent 1'
        
        datos_actividad = [
            ('Código', actividad.codigo or 'No definido'),
            ('Nombre Corto', actividad.nombreCorto or 'Sin nombre'),
            ('Estado', actividad.get_estado_display()),
            ('Tipo', actividad.tipo.tipo_actividad if actividad.tipo else 'No definido'),
            ('Presupuesto', self._formatear_moneda(actividad.presupuesto)),
            ('Grado Ejecución', actividad.gradoEjecucion or 'No definido'),
            ('Fecha Inicio', self._formatear_fecha(actividad.fecha_inicio)),
            ('Fecha Cierre', self._formatear_fecha(actividad.fecha_cierre))
        ]
        
        for i, (campo, valor) in enumerate(datos_actividad):
            tabla_info.cell(i, 0).text = campo
            tabla_info.cell(i, 1).text = str(valor)
            tabla_info.cell(i, 0).paragraphs[0].runs[0].bold = True
        
        self.document.add_paragraph()
        
        # Descripción
        if actividad.descripcion:
            p_desc = self.document.add_paragraph()
            p_desc.add_run('Descripción: ').bold = True
            p_desc.add_run(actividad.descripcion)
            self.document.add_paragraph()
        
        # Objetivo de la actividad
        if actividad.objetivo_de_actividad:
            p_obj = self.document.add_paragraph()
            p_obj.add_run('Objetivo: ').bold = True
            p_obj.add_run(actividad.objetivo_de_actividad)
            self.document.add_paragraph()
    
    def _agregar_vinculaciones_actividad(self, actividad):
        """Muestra las vinculaciones de la actividad mediante estructuraProcedencia"""
        
        estructura = actividad.estructuraProcedencia
        if not estructura:
            return
        
        self.document.add_paragraph('🔗 Vinculaciones:')
        
        datos_procedencia = estructura.get('datosProcedencia', {})
        vinculaciones = []
        
        mapeo_tipos = {
            'objetivogeneral': 'Objetivo General',
            'objetivoespecificoog': 'Objetivo Específico (OG)',
            'objetivoespecifico': 'Objetivo Específico',
            'indicadorog': 'Indicador OG',
            'indicadoroe': 'Indicador OE',
            'resultadoog': 'Resultado OG',
            'resultadooe': 'Resultado OE',
            'productooe': 'Producto OE',
            'productoroe': 'Producto ROE',
            'indicadorrog': 'Indicador ROG',
            'indicadorroe': 'Indicador ROE',
            'procesorog': 'Proceso ROG',
            'procesoroe': 'Proceso ROE',
            'procesopoe': 'Proceso POE'
        }
        
        for tipo, elemento in datos_procedencia.items():
            if elemento:
                nombre_tipo = mapeo_tipos.get(tipo, tipo)
                if isinstance(elemento, dict):
                    codigo = elemento.get('data', {}).get('codigo', 'No definido')
                    vinculaciones.append(f"• {nombre_tipo}: {codigo}")
                elif isinstance(elemento, list):
                    for elem in elemento:
                        if isinstance(elem, dict):
                            codigo = elem.get('data', {}).get('codigo', 'No definido')
                            vinculaciones.append(f"• {nombre_tipo}: {codigo}")
        
        for vinculacion in vinculaciones:
            self.document.add_paragraph(vinculacion, style='List Bullet')
        
        self.document.add_paragraph()
    
    def _agregar_tareas_actividad(self, actividad):
        """Agrega las tareas/subactividades de una actividad"""
        
        tareas = TareaActividad.objects.filter(actividad=actividad).order_by('fecha_creacion')
        if not tareas.exists():
            return
        
        self.document.add_heading('📝 Tareas/Subactividades', level=3)
        
        for i, tarea in enumerate(tareas, 1):
            self.document.add_heading(f'Tarea {i}: {tarea.codigo or "Sin código"}', level=4)
            
            # Información de la tarea
            tabla_tarea = self.document.add_table(rows=6, cols=2)
            tabla_tarea.style = 'Light Grid Accent 2'
            
            datos_tarea = [
                ('Código', tarea.codigo or 'No definido'),
                ('Título', tarea.titulo or 'Sin título'),
                ('Estado', tarea.get_estado_display()),
                ('Fecha Creación', self._formatear_fecha(tarea.fecha_creacion)),
                ('Fecha Ejecución', self._formatear_fecha(tarea.fecha_ejecucion)),
                ('Fecha Límite', self._formatear_fecha(tarea.fecha_limite))
            ]
            
            for j, (campo, valor) in enumerate(datos_tarea):
                tabla_tarea.cell(j, 0).text = campo
                tabla_tarea.cell(j, 1).text = str(valor)
                tabla_tarea.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            self.document.add_paragraph()
            
            # Descripción de la tarea
            if tarea.descripcion:
                p_desc_tarea = self.document.add_paragraph()
                p_desc_tarea.add_run('Descripción: ').bold = True
                p_desc_tarea.add_run(tarea.descripcion)
                self.document.add_paragraph()
            
            # Informes de la tarea
            self._agregar_informes_tarea(tarea)
            
            self.document.add_paragraph('―' * 50)
            self.document.add_paragraph()
    
    def _agregar_informes_actividad(self, actividad):
        """Agrega los informes de una actividad"""
        
        informes = InfActividad.objects.filter(actividad=actividad).order_by('fecha_ejecucion')
        if not informes.exists():
            return
        
        self.document.add_heading('📊 Informes de Actividad', level=3)
        
        for i, informe in enumerate(informes, 1):
            self.document.add_heading(f'Informe {i}: {informe.numeroInforme or "Sin número"}', level=4)
            
            # Información del informe
            tabla_informe = self.document.add_table(rows=5, cols=2)
            tabla_informe.style = 'Light Grid Accent 3'
            
            datos_informe = [
                ('Número de Informe', informe.numeroInforme or 'No definido'),
                ('Fecha de Ejecución', self._formatear_fecha(informe.fecha_ejecucion)),
                ('Tipo de Actividad', informe.tipo_actividad or 'No especificado'),
                ('Presupuesto Planificado', self._formatear_moneda(informe.presupuesto_planificado)),
                ('Presupuesto Ejecutado', self._formatear_moneda(informe.presupuesto_ejecutado)),
            ]
            
            for j, (campo, valor) in enumerate(datos_informe):
                tabla_informe.cell(j, 0).text = campo
                tabla_informe.cell(j, 1).text = str(valor)
                tabla_informe.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            self.document.add_paragraph()
            
            # Información adicional del informe
            if informe.objetivo_actividad:
                p_obj = self.document.add_paragraph()
                p_obj.add_run('Objetivo: ').bold = True
                p_obj.add_run(informe.objetivo_actividad)
            
            if informe.informe_objetivo_actividad:
                p_inf_obj = self.document.add_paragraph()
                p_inf_obj.add_run('Informe del Objetivo: ').bold = True
                p_inf_obj.add_run(informe.informe_objetivo_actividad)
            
            self.document.add_paragraph('―' * 40)
            self.document.add_paragraph()
    
    def _agregar_informes_tarea(self, tarea):
        """Agrega los informes de una tarea/subactividad"""
        
        informes = InfTarea.objects.filter(tarea=tarea).order_by('fecha_ejecucion')
        if not informes.exists():
            return
        
        self.document.add_heading('📋 Informes de la Tarea', level=5)
        
        for i, informe in enumerate(informes, 1):
            self.document.add_heading(f'Informe Tarea {i}: {informe.numeroInforme or "Sin número"}', level=6)
            
            # Información del informe de tarea
            tabla_informe = self.document.add_table(rows=5, cols=2)
            tabla_informe.style = 'Table Grid'
            
            datos_informe = [
                ('Número de Informe', informe.numeroInforme or 'No definido'),
                ('Fecha de Ejecución', self._formatear_fecha(informe.fecha_ejecucion)),
                ('Presupuesto Planificado', self._formatear_moneda(informe.presupuesto_planificado)),
                ('Presupuesto Ejecutado', self._formatear_moneda(informe.presupuesto_ejecutado)),
            ]
            
            for j, (campo, valor) in enumerate(datos_informe):
                tabla_informe.cell(j, 0).text = campo
                tabla_informe.cell(j, 1).text = str(valor)
                tabla_informe.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            self.document.add_paragraph()
            
            # Información adicional
            if informe.objetivo_tarea:
                p_obj = self.document.add_paragraph()
                p_obj.add_run('Objetivo: ').bold = True
                p_obj.add_run(informe.objetivo_tarea)
            
            self.document.add_paragraph('―' * 30)
            self.document.add_paragraph()

    # ============================================================================
    # MÉTODOS AUXILIARES PARA FORMATO
    # ============================================================================

    def _formatear_moneda(self, valor):
        """Formatea valores monetarios"""
        if valor is None:
            return "No definido"
        try:
            return f"${float(valor):,.2f}"
        except (TypeError, ValueError):
            return "Formato inválido"

    def _formatear_fecha(self, fecha):
        """Formatea fechas"""
        if not fecha:
            return "No definida"
        return fecha.strftime("%d/%m/%Y")

    # ============================================================================
    # MÉTODOS EXISTENTES (se mantienen igual)
    # ============================================================================

    def _agregar_indicadores_oe(self, objetivo_especifico):
        """Agrega indicadores relacionados al objetivo específico"""
        indicadores_oe = objetivo_especifico.indicador_oe.all()
        
        if not indicadores_oe.exists():
            self.document.add_heading('Indicadores del Objetivo Específico', level=2)
            p = self.document.add_paragraph()
            p.add_run("No se han definido indicadores para este objetivo específico.").italic = True
            self.document.add_paragraph()
            return
        
        self.document.add_heading('INDICADORES DEL OBJETIVO ESPECÍFICO', level=2)
        self.document.add_paragraph("Indicadores para medir el avance del objetivo específico:")
        
        for i, indicador in enumerate(indicadores_oe, 1):
            self.document.add_heading(f'Indicador {i}: {indicador.codigo}', level=3)
            
            # Tabla de información principal del indicador
            tabla_indicador = self.document.add_table(rows=8, cols=2)
            tabla_indicador.style = 'Light List Accent 3'
            
            datos_indicador = [
                ('Código', indicador.codigo or 'No definido'),
                ('Descripción', indicador.descripcion or 'No disponible'),
                ('Tipo', indicador.get_tipo_display() if indicador.tipo else 'No definido'),
                ('Frecuencia', indicador.get_frecuencia_display() if indicador.frecuencia else 'No definida'),
                ('Línea Base', indicador.baseline or 'No definida'),
                ('Meta Q1', indicador.target_q1 or 'No definida'),
                ('Fuente Verificación', indicador.fuente_verificacion or 'No definida'),
                ('Responsable', indicador.responsable or 'No asignado')
            ]
            
            for j, (campo, valor) in enumerate(datos_indicador):
                tabla_indicador.cell(j, 0).text = campo
                tabla_indicador.cell(j, 1).text = str(valor)
                tabla_indicador.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            self.document.add_paragraph()
            
            # Metas adicionales si existen
            metas_existen = any([
                indicador.target_q2, indicador.target_q3, indicador.target_q4
            ])
            
            if metas_existen:
                self.document.add_heading('Metas Adicionales', level=4)
                
                tabla_metas = self.document.add_table(rows=3, cols=2)
                tabla_metas.style = 'Light Grid Accent 4'
                
                metas = [
                    ('Meta Q2', indicador.target_q2),
                    ('Meta Q3', indicador.target_q3),
                    ('Meta Q4', indicador.target_q4)
                ]
                
                # Filtrar solo metas que existen
                metas_validas = [(periodo, meta) for periodo, meta in metas if meta]
                
                for k, (periodo, meta) in enumerate(metas_validas):
                    tabla_metas.cell(k, 0).text = periodo
                    tabla_metas.cell(k, 1).text = meta
                    tabla_metas.cell(k, 0).paragraphs[0].runs[0].bold = True
                
                self.document.add_paragraph()
            
            self.document.add_paragraph("―" * 40)
            self.document.add_paragraph()
    
    def _agregar_resultados_oe(self, objetivo_especifico, profundidad):
        """Agrega resultados relacionados al objetivo específico"""
        resultados_oe = objetivo_especifico.resultados_oe.all().prefetch_related(
            'indicador_res_oe',
            'productos_res_oe'
        )
        
        if not resultados_oe.exists():
            self.document.add_heading('Resultados del Objetivo Específico', level=2)
            p = self.document.add_paragraph()
            p.add_run("No se han definido resultados para este objetivo específico.").italic = True
            self.document.add_paragraph()
            return
        
        self.document.add_heading('RESULTADOS DEL OBJETIVO ESPECÍFICO', level=2)
        
        for i, resultado in enumerate(resultados_oe, 1):
            self.document.add_heading(f'Resultado {i}: {resultado.codigo}', level=3)
            
            tabla_resultado = self.document.add_table(rows=4, cols=2)
            tabla_resultado.style = 'Light List Accent 4'
            
            datos_resultado = [
                ('Código', resultado.codigo or 'No definido'),
                ('Descripción', resultado.descripcion or 'No disponible'),
                ('Supuestos', resultado.supuestos or 'No definidos'),
                ('Riesgos', resultado.riesgos or 'No identificados')
            ]
            
            for j, (campo, valor) in enumerate(datos_resultado):
                tabla_resultado.cell(j, 0).text = campo
                tabla_resultado.cell(j, 1).text = str(valor)
                tabla_resultado.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            self.document.add_paragraph()
            
            # ENCADENAR niveles inferiores si hay profundidad > 2
            if profundidad > 2:
                self._agregar_nivel_inferior_resultado_oe(resultado)
            
            self.document.add_paragraph("―" * 40)
            self.document.add_paragraph()
    
    def _agregar_productos_oe(self, objetivo_especifico, profundidad):
        """Agrega productos relacionados al objetivo específico"""
        productos_oe = objetivo_especifico.productos_oe.all().prefetch_related(
            'proceso_producto_oe'
        )
        
        if not productos_oe.exists():
            self.document.add_heading('Productos del Objetivo Específico', level=2)
            p = self.document.add_paragraph()
            p.add_run("No se han definido productos para este objetivo específico.").italic = True
            self.document.add_paragraph()
            return
        
        self.document.add_heading('PRODUCTOS DEL OBJETIVO ESPECÍFICO', level=2)
        
        for i, producto in enumerate(productos_oe, 1):
            self.document.add_heading(f'Producto {i}: {producto.codigo}', level=3)
            
            tabla_producto = self.document.add_table(rows=5, cols=2)
            tabla_producto.style = 'Light List Accent 5'
            
            datos_producto = [
                ('Código', producto.codigo or 'No definido'),
                ('Descripción', producto.descripcion or 'No disponible'),
                ('Supuestos', producto.supuestos or 'No definidos'),
                ('Riesgos', producto.riesgos or 'No identificados'),
                ('Entregado', 'Sí' if producto.entregado else 'No')
            ]
            
            for j, (campo, valor) in enumerate(datos_producto):
                tabla_producto.cell(j, 0).text = campo
                tabla_producto.cell(j, 1).text = str(valor)
                tabla_producto.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            self.document.add_paragraph()
            
            # ENCADENAR procesos del producto si hay profundidad > 2
            if profundidad > 2:
                self._agregar_procesos_producto_oe(producto)
            
            self.document.add_paragraph("―" * 40)
            self.document.add_paragraph()
    
    def _agregar_nivel_inferior_resultado_oe(self, resultado_oe):
        """Agrega nivel inferior para resultado OE: Indicadores y Productos"""
        
        # Indicadores ROE
        indicadores_roe = resultado_oe.indicador_res_oe.all()
        if indicadores_roe.exists():
            self.document.add_heading('Indicadores del Resultado OE', level=4)
            
            for indicador in indicadores_roe:
                self.document.add_heading(f'Indicador: {indicador.codigo}', level=5)
                
                tabla_indicador = self.document.add_table(rows=6, cols=2)
                tabla_indicador.style = 'Table Grid'
                
                datos_indicador = [
                    ('Código', indicador.codigo or 'No definido'),
                    ('Descripción', indicador.descripcion or 'No disponible'),
                    ('Línea Base', indicador.baseline or 'No definida'),
                    ('Meta Q1', indicador.target_q1 or 'No definida'),
                    ('Fuente Verificación', indicador.fuente_verificacion or 'No definida'),
                    ('Responsable', indicador.responsable or 'No asignado')
                ]
                
                for i, (campo, valor) in enumerate(datos_indicador):
                    tabla_indicador.cell(i, 0).text = campo
                    tabla_indicador.cell(i, 1).text = str(valor)
                    tabla_indicador.cell(i, 0).paragraphs[0].runs[0].bold = True
                
                self.document.add_paragraph()
        
        # Productos ROE
        productos_roe = resultado_oe.productos_res_oe.all()
        if productos_roe.exists():
            self.document.add_heading('Productos del Resultado OE', level=4)
            
            for producto in productos_roe:
                self.document.add_heading(f'Producto: {producto.codigo}', level=5)
                
                tabla_producto = self.document.add_table(rows=4, cols=2)
                tabla_producto.style = 'Table Grid'
                
                datos_producto = [
                    ('Código', producto.codigo or 'No definido'),
                    ('Descripción', producto.descripcion or 'No disponible'),
                    ('Supuestos', producto.supuestos or 'No definidos'),
                    ('Entregado', '✅ Sí' if producto.entregado else '⏳ No')
                ]
                
                for i, (campo, valor) in enumerate(datos_producto):
                    tabla_producto.cell(i, 0).text = campo
                    tabla_producto.cell(i, 1).text = str(valor)
                    tabla_producto.cell(i, 0).paragraphs[0].runs[0].bold = True
                
                self.document.add_paragraph()
    
    def _agregar_procesos_producto_oe(self, producto_oe):
        """Agrega procesos relacionados al producto OE"""
        procesos_poe = producto_oe.proceso_producto_oe.all()
        
        if procesos_poe.exists():
            self.document.add_heading('Procesos del Producto', level=4)
            
            for proceso in procesos_poe:
                self.document.add_heading(f'Proceso: {proceso.codigo}', level=5)
                
                tabla_proceso = self.document.add_table(rows=3, cols=2)
                tabla_proceso.style = 'Table Grid'
                
                datos_proceso = [
                    ('Código', proceso.codigo or 'No definido'),
                    ('Título', proceso.titulo or 'No disponible'),
                    ('Descripción', proceso.descripcion or 'No disponible')
                ]
                
                for i, (campo, valor) in enumerate(datos_proceso):
                    tabla_proceso.cell(i, 0).text = campo
                    tabla_proceso.cell(i, 1).text = str(valor)
                    tabla_proceso.cell(i, 0).paragraphs[0].runs[0].bold = True
                
                self.document.add_paragraph()

    def _agregar_portada(self, objetivo_especifico):
        """Portada del reporte de objetivo específico"""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        titulo = self.document.add_heading('REPORTE DE OBJETIVO ESPECÍFICO', 0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        self.document.add_paragraph()
        
        # Información principal de portada - MANEJO SEGURO de None
        info_portada = [
            ('Código del Objetivo:', objetivo_especifico.codigo),
            ('Objetivo General:', self._obtener_codigo_objetivo_general(objetivo_especifico)),
            ('Proyecto:', self._obtener_info_proyecto(objetivo_especifico)),
        ]
        
        for etiqueta, valor in info_portada:
            if valor:
                p = self.document.add_paragraph()
                p.add_run(etiqueta).bold = True
                p.add_run(f' {valor}')
        
        self.document.add_page_break()
    
    def _obtener_codigo_objetivo_general(self, objetivo_especifico):
        """Obtiene el código del objetivo general de forma segura"""
        if objetivo_especifico.objetivo_general and objetivo_especifico.objetivo_general.codigo:
            return objetivo_especifico.objetivo_general.codigo
        return 'No vinculado a objetivo general'
    
    def _obtener_info_proyecto(self, objetivo_especifico):
        """Obtiene información del proyecto de forma segura"""
        if objetivo_especifico.proyecto:
            return f"{objetivo_especifico.proyecto.codigo} - {objetivo_especifico.proyecto.titulo}"
        return 'Proyecto no asignado'
    
    def _agregar_informacion_principal(self, objetivo_especifico):
        """Sección de información principal"""
        self._agregar_seccion('INFORMACIÓN PRINCIPAL', 1)
        
        # Determinar tipo de objetivo específico
        tipo_objetivo = 'Objetivo Específico de Objetivo General' if objetivo_especifico.objetivo_general else 'Objetivo Específico Directo del Proyecto'
        
        datos_principales = [
            ('Código', objetivo_especifico.codigo or 'No definido'),
            ('Descripción', objetivo_especifico.descripcion or 'No disponible'),
            ('Tipo', tipo_objetivo),
            ('Nivel', 'Operativo/Táctico')
        ]
        
        self._agregar_tabla_datos('Datos del Objetivo Específico', datos_principales)
    
    def _agregar_analisis_riesgos(self, objetivo_especifico):
        """Sección de análisis de riesgos y supuestos"""
        self._agregar_seccion('ANÁLISIS OPERATIVO', 1)
        
        # Supuestos
        if objetivo_especifico.supuestos:
            self.document.add_heading('Supuestos Operativos', level=2)
            p_supuestos = self.document.add_paragraph(objetivo_especifico.supuestos)
            p_supuestos.style = 'List Bullet'
            self.document.add_paragraph()
        
        # Riesgos
        if objetivo_especifico.riesgos:
            self.document.add_heading('Riesgos Operativos', level=2)
            p_riesgos = self.document.add_paragraph(objetivo_especifico.riesgos)
            p_riesgos.style = 'List Bullet'
            self.document.add_paragraph()
        
        # Si no hay información
        if not objetivo_especifico.supuestos and not objetivo_especifico.riesgos:
            p = self.document.add_paragraph()
            p.add_run('No se han definido supuestos ni riesgos para este objetivo específico.').italic = True
    
    def _agregar_vinculaciones(self, objetivo_especifico):
        """Sección de vinculaciones"""
        self._agregar_seccion('VINCULACIONES', 1)
        
        vinculaciones = []
        
        # Objetivo General
        if objetivo_especifico.objetivo_general:
            desc_og = objetivo_especifico.objetivo_general.descripcion
            vinculaciones.append(('Objetivo General', 
                                f"{objetivo_especifico.objetivo_general.codigo} - {desc_og[:50]}..." if desc_og else objetivo_especifico.objetivo_general.codigo))
        else:
            vinculaciones.append(('Objetivo General', 'No vinculado'))
        
        # Proyecto
        if objetivo_especifico.proyecto:
            vinculaciones.append(('Proyecto', 
                                f"{objetivo_especifico.proyecto.codigo} - {objetivo_especifico.proyecto.titulo}"))
        else:
            vinculaciones.append(('Proyecto', 'No asignado'))
        
        if vinculaciones:
            self._agregar_tabla_datos('Relaciones del Objetivo', vinculaciones)
    
    def generar_y_descargar_individual(self, objetivo_especifico_id):
        """Genera y descarga SOLO el objetivo específico"""
        buffer = self.generar_reporte_objetivo_especifico_og(objetivo_especifico_id)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="reporte_objetivo_especifico_{objetivo_especifico_id}.docx"'
        
        return response