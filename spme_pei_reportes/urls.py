# spme_pei_reportes/urls.py
from django.urls import path
from .views.pei_report_view import pei_report_word
from .views.objetivo_report_view import objetivo_report_word
from .views.factor_report_view import factor_report_word
from .views.indicador_report_view import indicador_report_word
from .views.reporte_encadenado_view import reporte_encadenado_word

app_name = 'spme_pei_reportes'

urlpatterns = [
    # Se irán agregando rutas en cada hito
    path(r'pei/<int:pei_id>/word/', pei_report_word, name='pei-report-word'),
    path(r'objetivo/<int:objetivo_id>/word/', objetivo_report_word, name='objetivo-report-word'),
    path(r'factor/<int:factor_id>/word/', factor_report_word, name='factor-report-word'),
    path(r'indicador/<int:indicador_id>/word/', indicador_report_word, name='indicador-report-word'),
    path(r'encadenado/<str:tipo>/<int:elemento_id>/word/', reporte_encadenado_word, name='reporte-encadenado-word'),
]