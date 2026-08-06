"""
Rutas de spme_tree_reporter.
"""

from django.urls import path
from .views.generar_reporte_proyecto_view import GenerarReporteProyectoView

urlpatterns = [
    path(r'reportes/generar/', GenerarReporteProyectoView.as_view(), name='reporte-tree-generar'),
]