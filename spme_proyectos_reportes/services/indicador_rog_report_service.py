def generar_indicadores_rog(doc, resultado_og):
    doc.add_heading(f"Indicadores del Resultado ({resultado_og.codigo or '-'})", level=3)

    indicadores = resultado_og.indicador_res_og.all()
    if not indicadores.exists():
        doc.add_paragraph("No existen indicadores para este resultado.")
        return

    for ind in indicadores:
        doc.add_paragraph(f"• {ind.codigo or '-'} - {ind.descripcion or 'Sin descripción'}", style="List Bullet")
        doc.add_paragraph(f"   Tipo: {ind.get_tipo_display()}")
        doc.add_paragraph(f"   Frecuencia: {ind.get_frecuencia_display()}")
        if ind.baseline:
            doc.add_paragraph(f"   Línea base: {ind.baseline}")
        if ind.target_q4:
            doc.add_paragraph(f"   Meta final: {ind.target_q4}")
        doc.add_paragraph()
