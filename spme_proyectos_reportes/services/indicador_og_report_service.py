def generar_indicadores_og(doc, objetivo_general):
    doc.add_heading("Indicadores del Objetivo General", level=2)

    indicadores = objetivo_general.indicador_og.all()
    if not indicadores.exists():
        doc.add_paragraph("No existen indicadores asociados.")
        return

    for ind in indicadores:
        doc.add_paragraph(f"• {ind.codigo or '-'} - {ind.descripcion or 'Sin descripción'}", style="List Bullet")
        doc.add_paragraph(f"   Tipo: {ind.get_tipo_display()}")
        doc.add_paragraph(f"   Frecuencia: {ind.get_frecuencia_display()}")
        if ind.fuente_verificacion:
            doc.add_paragraph(f"   Fuente de verificación: {ind.fuente_verificacion}")
        if ind.baseline:
            doc.add_paragraph(f"   Línea base: {ind.baseline}")
        if ind.target_q4:
            doc.add_paragraph(f"   Meta final: {ind.target_q4}")
        doc.add_paragraph()
