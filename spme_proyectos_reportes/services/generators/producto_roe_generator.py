#from .base_generator import BaseGenerator
from ..base.base_report_service import BaseReportService
from spme_estructuracion_proyecto.models import ProductoResultadoOE

class ProductoROEGenerator(BaseReportService):
    """Generador para Productos de Resultado OE (Nivel 5)"""
    
    def _agregar_portada(self, producto_roe):
        """Agrega portada del producto ROE"""
        # Título principal
        title = self.document.add_heading('REPORTE DE PRODUCTO DE RESULTADO OE', 0)
        title.alignment = 1  # Centrado
        
        # Información básica
        self.document.add_heading(producto_roe.codigo or 'Producto sin código', level=1)
        
        # Información de identificación
        info_paragraph = self.document.add_paragraph()
        info_paragraph.add_run("Código: ").bold = True
        info_paragraph.add_run(producto_roe.codigo or "No definido")
        
        info_paragraph = self.document.add_paragraph()
        info_paragraph.add_run("Tipo: ").bold = True
        info_paragraph.add_run("Producto de Resultado OE")
        
        if producto_roe.resultado_oe and producto_roe.resultado_oe.codigo:
            info_paragraph = self.document.add_paragraph()
            info_paragraph.add_run("Resultado OE Asociado: ").bold = True
            info_paragraph.add_run(producto_roe.resultado_oe.codigo)
        
        self.document.add_page_break()
    
    def _agregar_informacion_principal(self, producto_roe):
        """Agrega información principal del producto ROE"""
        self.document.add_heading('INFORMACIÓN PRINCIPAL', level=1)
        
        # Tabla de datos principales
        tabla_principal = self.document.add_table(rows=6, cols=2)
        tabla_principal.style = 'Light Grid Accent 1'
        
        datos_principales = [
            ('Código', producto_roe.codigo or 'No definido'),
            ('Descripción', producto_roe.descripcion or 'No disponible'),
            ('Estado de Entrega', '✅ ENTREGADO' if producto_roe.entregado else '⏳ PENDIENTE'),
            ('Supuestos', producto_roe.supuestos or 'No definidos'),
            ('Riesgos', producto_roe.riesgos or 'No identificados'),
            ('Resultado OE Asociado', 
            f"{producto_roe.resultado_oe.codigo} - {producto_roe.resultado_oe.descripcion[:100]}..." 
            if producto_roe.resultado_oe else 'No asociado')
        ]
        
        for i, (campo, valor) in enumerate(datos_principales):
            tabla_principal.cell(i, 0).text = str(campo)
            tabla_principal.cell(i, 1).text = str(valor)
            tabla_principal.cell(i, 0).paragraphs[0].runs[0].bold = True
        
        self.document.add_paragraph()
    
    def _agregar_detalles_entrega(self, producto_roe):
        """Agrega detalles específicos de entrega"""
        self.document.add_heading('DETALLES DE ENTREGA', level=2)
        
        estado_entrega = "ENTREGADO" if producto_roe.entregado else "PENDIENTE"
        icono = "✅" if producto_roe.entregado else "⏳"
        
        p_estado = self.document.add_paragraph()
        p_estado.add_run(f"{icono} Estado de Entrega: ").bold = True
        p_estado.add_run(estado_entrega)
        
        if producto_roe.entregado:
            p_entregado = self.document.add_paragraph()
            p_entregado.add_run("🎉 ").bold = True
            p_entregado.add_run("Este producto ha sido marcado como entregado.")
        else:
            p_pendiente = self.document.add_paragraph()
            p_pendiente.add_run("📋 ").bold = True
            p_pendiente.add_run("Este producto está pendiente de entrega.")
        
        self.document.add_paragraph()
    
    def _agregar_analisis_riesgos_supuestos(self, producto_roe):
        """Agrega análisis de riesgos y supuestos"""
        # Supuestos
        self.document.add_heading('SUPUESTOS', level=2)
        if producto_roe.supuestos:
            p_supuestos = self.document.add_paragraph()
            p_supuestos.add_run("📝 ").bold = True
            p_supuestos.add_run("Supuestos considerados para este producto:")
            self.document.add_paragraph(producto_roe.supuestos)
        else:
            p_no_supuestos = self.document.add_paragraph()
            p_no_supuestos.add_run("No se han definido supuestos para este producto.").italic = True
        
        # Riesgos
        self.document.add_heading('RIESGOS', level=2)
        if producto_roe.riesgos:
            p_riesgos = self.document.add_paragraph()
            p_riesgos.add_run("⚠️ ").bold = True
            p_riesgos.add_run("Riesgos identificados para este producto:")
            self.document.add_paragraph(producto_roe.riesgos)
        else:
            p_no_riesgos = self.document.add_paragraph()
            p_no_riesgos.add_run("No se han identificado riesgos para este producto.").italic = True
        
        self.document.add_paragraph()
    
    def _agregar_contexto_resultado(self, producto_roe):
        """Agrega información del resultado OE padre"""
        if producto_roe.resultado_oe:
            self.document.add_heading('CONTEXTO DEL RESULTADO OE', level=2)
            
            tabla_contexto = self.document.add_table(rows=4, cols=2)
            tabla_contexto.style = 'Light List Accent 2'
            
            datos_contexto = [
                ('Código Resultado OE', producto_roe.resultado_oe.codigo or 'No definido'),
                ('Descripción Resultado OE', producto_roe.resultado_oe.descripcion or 'No disponible'),
                ('Supuestos Resultado OE', producto_roe.resultado_oe.supuestos or 'No definidos'),
                ('Riesgos Resultado OE', producto_roe.resultado_oe.riesgos or 'No identificados')
            ]
            
            for i, (campo, valor) in enumerate(datos_contexto):
                tabla_contexto.cell(i, 0).text = str(campo)
                tabla_contexto.cell(i, 1).text = str(valor)
                tabla_contexto.cell(i, 0).paragraphs[0].runs[0].bold = True
            
            self.document.add_paragraph()
    
    def _agregar_resumen_impacto(self, producto_roe):
        """Agrega resumen del impacto del producto"""
        self.document.add_heading('RESUMEN E IMPACTO', level=2)
        
        p_impacto = self.document.add_paragraph()
        p_impacto.add_run("🎯 ").bold = True
        p_impacto.add_run("Impacto esperado: ")
        
        if producto_roe.descripcion:
            p_impacto.add_run("Este producto contribuye directamente al logro del resultado OE asociado.")
        else:
            p_impacto.add_run("Producto esencial para el cumplimiento del resultado operativo.")
        
        # Estado visual
        p_estado_visual = self.document.add_paragraph()
        p_estado_visual.add_run("📊 Estado actual: ").bold = True
        if producto_roe.entregado:
            p_estado_visual.add_run("COMPLETADO - Producto entregado y verificado.")
        else:
            p_estado_visual.add_run("EN PROCESO - Producto en desarrollo o pendiente de entrega.")
        
        self.document.add_paragraph()
    
    def generar_reporte_producto_roe(self, producto_roe_id):
        """Genera reporte completo del producto ROE"""
        try:
            # Obtener el producto ROE con relaciones
            producto_roe = ProductoResultadoOE.objects.select_related('resultado_oe').get(id=producto_roe_id)
            
            # Construir el reporte
            self._agregar_portada(producto_roe)
            self._agregar_informacion_principal(producto_roe)
            self._agregar_detalles_entrega(producto_roe)
            self._agregar_analisis_riesgos_supuestos(producto_roe)
            self._agregar_contexto_resultado(producto_roe)
            self._agregar_resumen_impacto(producto_roe)
            
            return self._guardar_documento()
            
        except ProductoResultadoOE.DoesNotExist:
            raise ValueError(f"ProductoResultadoOE con ID {producto_roe_id} no encontrado")
        except Exception as e:
            raise ValueError(f"Error generando reporte de Producto ROE: {str(e)}")