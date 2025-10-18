from ..base.base_report_service import BaseReportService
from spme_estructuracion_proyecto.models import Proceso

class ProcesoGenerator(BaseReportService):
    """Generador para Procesos (Niveles 4-5)"""
    
    def _agregar_portada(self, proceso, tipo_proceso):
        """Agrega portada del proceso"""
        tipo_display = {
            'procesorog': 'Proceso de Resultado OG',
            'procesoroe': 'Proceso de Resultado OE', 
            'procesopoe': 'Proceso de Producto OE'
        }.get(tipo_proceso, 'Proceso')
        
        title = self.document.add_heading(f'REPORTE DE {tipo_display.upper()}', 0)
        title.alignment = 1  # Centrado
        
        self.document.add_heading(proceso.codigo or 'Proceso sin código', level=1)
        
        # Información de identificación
        info_paragraph = self.document.add_paragraph()
        info_paragraph.add_run("Código: ").bold = True
        info_paragraph.add_run(proceso.codigo or "No definido")
        
        info_paragraph = self.document.add_paragraph()
        info_paragraph.add_run("Tipo: ").bold = True
        info_paragraph.add_run(tipo_display)
        
        info_paragraph = self.document.add_paragraph()
        info_paragraph.add_run("Título: ").bold = True
        info_paragraph.add_run(proceso.titulo or "No disponible")
        
        self.document.add_page_break()
    
    def _agregar_informacion_principal(self, proceso, tipo_proceso):
        """Agrega información principal del proceso"""
        self.document.add_heading('INFORMACIÓN PRINCIPAL', level=1)
        
        # Determinar elemento padre
        elemento_padre = None
        elemento_tipo = None
        
        if proceso.resultado_og:
            elemento_padre = f"{proceso.resultado_og.codigo} - {proceso.resultado_og.descripcion[:100]}..."
            elemento_tipo = "Resultado OG"
        elif proceso.resultado_oe:
            elemento_padre = f"{proceso.resultado_oe.codigo} - {proceso.resultado_oe.descripcion[:100]}..."
            elemento_tipo = "Resultado OE"
        elif proceso.producto_oe:
            elemento_padre = f"{proceso.producto_oe.codigo} - {proceso.producto_oe.descripcion[:100]}..."
            elemento_tipo = "Producto OE"
        
        # Tabla de datos principales
        tabla_principal = self.document.add_table(rows=5, cols=2)
        tabla_principal.style = 'Light Grid Accent 1'
        
        datos_principales = [
            ('Código', proceso.codigo or 'No definido'),
            ('Título', proceso.titulo or 'No disponible'),
            ('Descripción', proceso.descripcion or 'No disponible'),
            ('Elemento Padre', elemento_padre or 'No asociado'),
            ('Tipo de Elemento Padre', elemento_tipo or 'No definido')
        ]
        
        for i, (campo, valor) in enumerate(datos_principales):
            tabla_principal.cell(i, 0).text = str(campo)
            tabla_principal.cell(i, 1).text = str(valor)
            tabla_principal.cell(i, 0).paragraphs[0].runs[0].bold = True
        
        self.document.add_paragraph()
    
    def _agregar_contexto_elemento_padre(self, proceso):
        """Agrega información del elemento padre"""
        if proceso.resultado_og:
            self._agregar_contexto_resultado_og(proceso.resultado_og)
        elif proceso.resultado_oe:
            self._agregar_contexto_resultado_oe(proceso.resultado_oe)
        elif proceso.producto_oe:
            self._agregar_contexto_producto_oe(proceso.producto_oe)
    
    def _agregar_contexto_resultado_og(self, resultado_og):
        """Agrega contexto del Resultado OG padre"""
        self.document.add_heading('CONTEXTO: RESULTADO OG PADRE', level=2)
        
        tabla_contexto = self.document.add_table(rows=4, cols=2)
        tabla_contexto.style = 'Light List Accent 2'
        
        datos_contexto = [
            ('Código', resultado_og.codigo or 'No definido'),
            ('Descripción', resultado_og.descripcion or 'No disponible'),
            ('Supuestos', resultado_og.supuestos or 'No definidos'),
            ('Riesgos', resultado_og.riesgos or 'No identificados')
        ]
        
        for i, (campo, valor) in enumerate(datos_contexto):
            tabla_contexto.cell(i, 0).text = str(campo)
            tabla_contexto.cell(i, 1).text = str(valor)
            tabla_contexto.cell(i, 0).paragraphs[0].runs[0].bold = True
        
        self.document.add_paragraph()
    
    def _agregar_contexto_resultado_oe(self, resultado_oe):
        """Agrega contexto del Resultado OE padre"""
        self.document.add_heading('CONTEXTO: RESULTADO OE PADRE', level=2)
        
        tabla_contexto = self.document.add_table(rows=4, cols=2)
        tabla_contexto.style = 'Light List Accent 3'
        
        datos_contexto = [
            ('Código', resultado_oe.codigo or 'No definido'),
            ('Descripción', resultado_oe.descripcion or 'No disponible'),
            ('Supuestos', resultado_oe.supuestos or 'No definidos'),
            ('Riesgos', resultado_oe.riesgos or 'No identificados')
        ]
        
        for i, (campo, valor) in enumerate(datos_contexto):
            tabla_contexto.cell(i, 0).text = str(campo)
            tabla_contexto.cell(i, 1).text = str(valor)
            tabla_contexto.cell(i, 0).paragraphs[0].runs[0].bold = True
        
        self.document.add_paragraph()
    
    def _agregar_contexto_producto_oe(self, producto_oe):
        """Agrega contexto del Producto OE padre"""
        self.document.add_heading('CONTEXTO: PRODUCTO OE PADRE', level=2)
        
        tabla_contexto = self.document.add_table(rows=5, cols=2)
        tabla_contexto.style = 'Light List Accent 4'
        
        datos_contexto = [
            ('Código', producto_oe.codigo or 'No definido'),
            ('Descripción', producto_oe.descripcion or 'No disponible'),
            ('Supuestos', producto_oe.supuestos or 'No definidos'),
            ('Riesgos', producto_oe.riesgos or 'No identificados'),
            ('Entregado', '✅ Sí' if producto_oe.entregado else '⏳ No')
        ]
        
        for i, (campo, valor) in enumerate(datos_contexto):
            tabla_contexto.cell(i, 0).text = str(campo)
            tabla_contexto.cell(i, 1).text = str(valor)
            tabla_contexto.cell(i, 0).paragraphs[0].runs[0].bold = True
        
        self.document.add_paragraph()
    
    def _agregar_resumen_impacto(self, proceso, tipo_proceso):
        """Agrega resumen del impacto del proceso"""
        self.document.add_heading('IMPACTO Y ALCANCE', level=2)
        
        p_impacto = self.document.add_paragraph()
        p_impacto.add_run("🎯 ").bold = True
        p_impacto.add_run("Contribución del proceso: ")
        
        if tipo_proceso == 'procesorog':
            p_impacto.add_run("Este proceso es esencial para alcanzar el Resultado OG asociado.")
        elif tipo_proceso == 'procesoroe':
            p_impacto.add_run("Este proceso contribuye directamente al logro del Resultado OE.")
        elif tipo_proceso == 'procesopoe':
            p_impacto.add_run("Este proceso es necesario para la entrega del Producto OE.")
        else:
            p_impacto.add_run("Proceso operativo clave para el cumplimiento de objetivos.")
        
        # Detalles específicos
        p_detalles = self.document.add_paragraph()
        p_detalles.add_run("📋 ").bold = True
        p_detalles.add_run("Alcance: ")
        
        if proceso.descripcion:
            p_detalles.add_run(proceso.descripcion[:200] + "...")
        else:
            p_detalles.add_run("Proceso definido para soportar actividades específicas.")
        
        self.document.add_paragraph()
    
    def generar_reporte_proceso(self, proceso_id, tipo_proceso):
        """Genera reporte completo del proceso"""
        try:
            # Obtener el proceso con relaciones
            proceso = Proceso.objects.select_related(
                'resultado_og', 'resultado_oe', 'producto_oe'
            ).get(id=proceso_id)
            
            # Construir el reporte
            self._agregar_portada(proceso, tipo_proceso)
            self._agregar_informacion_principal(proceso, tipo_proceso)
            self._agregar_contexto_elemento_padre(proceso)
            self._agregar_resumen_impacto(proceso, tipo_proceso)
            
            return self._guardar_documento()
            
        except Proceso.DoesNotExist:
            raise ValueError(f"Proceso con ID {proceso_id} no encontrado")
        except Exception as e:
            raise ValueError(f"Error generando reporte de proceso: {str(e)}")