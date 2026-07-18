# spme/spme_email/views/email_test_views.py
from django.views import View
from django.shortcuts import render
from datetime import datetime


class PreviewEmailView(View):
    """
    Endpoint para previsualizar templates de email en el navegador.
    
    URLs:
        GET /api-mail/email/preview/test-estilos/
        GET /api-mail/email/preview/peticion-revision/
    
    Jerarquía de directorios:
        templates/
        └── correos/
            ├── base_correo.html
            ├── sistema/
            │   ├── formularios/
            │   │   ├── solicitudFondos/
            │   │   │   └── peticion_revision.html
            │   │   ├── solicitudPagoDirecto/
            │   │   └── solicitudViaje/
            │   └── preview_error.html
            └── tests/
                └── test_estilos.html
    """
    
    # Mapeo de templates a sus rutas y contextos
    TEMPLATES_CONFIG = {
        # En PreviewEmailView.TEMPLATES_CONFIG

        # Solicitud de Fondos - Actividad (sin tarea)
        'peticion_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudFondos/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SF 00020',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '30.00',
                'fecha_solicitud': '2026-03-26',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=20',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },

        # Solicitud de Fondos - Subactividad (con tarea)
        'peticion_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudFondos/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SF 00021',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '20.00',
                'fecha_solicitud': '2026-03-27',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=21&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },

        # Solicitud de Fondos Aprobada - Actividad
        'aprobacion_actividad': {
            'path': 'correos/sistema/formularios/solicitudFondos/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SF 00020',
                'monto': '30.00',
                'fecha_aprobacion': '2026-03-28',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=20',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },
         # Solicitud de Fondos Aprobada - Subactividad
        'aprobacion_tarea': {
            'path': 'correos/sistema/formularios/solicitudFondos/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SF 00021',
                'monto': '20.00',
                'fecha_aprobacion': '2026-03-29',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=21&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },

        # Solicitud de Fondos Rechazada - Actividad
        'rechazo_actividad': {
            'path': 'correos/sistema/formularios/solicitudFondos/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SF 00020',
                'monto': '30.00',
                'fecha_rechazo': '2026-03-28',
                'motivo_rechazo': 'El monto solicitado excede el presupuesto disponible para esta actividad.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=20',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },

        # Solicitud de Fondos Rechazada - Subactividad
        'rechazo_tarea': {
            'path': 'correos/sistema/formularios/solicitudFondos/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SF 00021',
                'monto': '20.00',
                'fecha_rechazo': '2026-03-29',
                'motivo_rechazo': 'Falta detallar la descripción de la subactividad.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=21&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Actividad
        'nueva_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudFondos/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'ACT0003-CP-CD - SF 00020',
                'monto': '25.00',
                'fecha_correccion': '2026-03-30',
                'motivo_rechazo': 'El monto solicitado excede el presupuesto disponible para esta actividad.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=20',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Subactividad
        'nueva_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudFondos/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'ACT0003-CP-CD - SF 00021',
                'monto': '20.00',
                'fecha_correccion': '2026-03-30',
                'motivo_rechazo': 'Falta detallar la descripción de la subactividad.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario011/89?solicitud_id=21&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Fondos',
                'current_year': datetime.now().year,
            }
        },

        # ============================================================
        # SOLICITUD DE REPOSICIÓN (REEMBOLSO)
        # ============================================================

        # Petición Revisión - Actividad
        'reposicion_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudReembolso/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD- SR0016',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '450.00',
                'fecha_solicitud': '2026-06-03',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=16',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },

        # Petición Revisión - Subactividad
        'reposicion_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudReembolso/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD- SR0017',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '250.00',
                'fecha_solicitud': '2026-06-03',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=17&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Actividad
        'reposicion_aprobacion_actividad': {
            'path': 'correos/sistema/formularios/solicitudReembolso/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD- SR0016',
                'monto': '450.00',
                'fecha_aprobacion': '2026-06-05',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=16',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Subactividad
        'reposicion_aprobacion_tarea': {
            'path': 'correos/sistema/formularios/solicitudReembolso/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD- SR0017',
                'monto': '250.00',
                'fecha_aprobacion': '2026-06-05',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=17&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Actividad
        'reposicion_rechazo_actividad': {
            'path': 'correos/sistema/formularios/solicitudReembolso/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD- SR0016',
                'monto': '450.00',
                'fecha_rechazo': '2026-06-04',
                'motivo_rechazo': 'Los comprobantes presentados no corresponden al período de la actividad.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=16',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Subactividad
        'reposicion_rechazo_tarea': {
            'path': 'correos/sistema/formularios/solicitudReembolso/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD- SR0017',
                'monto': '250.00',
                'fecha_rechazo': '2026-06-04',
                'motivo_rechazo': 'Falta adjuntar factura del servicio de transporte.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=17&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Actividad
        'reposicion_nueva_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudReembolso/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'ACT0003-CP-CD- SR0016',
                'monto': '450.00',
                'fecha_correccion': '2026-06-06',
                'motivo_rechazo': 'Los comprobantes presentados no corresponden al período de la actividad.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=16',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Subactividad
        'reposicion_nueva_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudReembolso/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'ACT0003-CP-CD- SR0017',
                'monto': '250.00',
                'fecha_correccion': '2026-06-06',
                'motivo_rechazo': 'Falta adjuntar factura del servicio de transporte.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario033/89?solicitud_id=17&tarea_id=26',
                'accion_url_texto': 'Ir a la Solicitud de Reposicion',
                'current_year': datetime.now().year,
            }
        },
        # ============================================================
        # SOLICITUD DE VIAJE
        # ============================================================

        # Petición Revisión - Actividad
        'viaje_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudViaje/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'SV-202605-D55229B7',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '300.00',
                'fecha_solicitud': '2026-05-20',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },

        # Petición Revisión - Subactividad
        'viaje_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudViaje/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'SV-202604-88CDE154',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '1000.00',
                'fecha_solicitud': '2026-04-24',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0027/ACT0003-CP-CD - Tarea',
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=26&tarea_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Actividad
        'viaje_aprobacion_actividad': {
            'path': 'correos/sistema/formularios/solicitudViaje/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'SV-202605-D55229B7',
                'monto': '300.00',
                'fecha_aprobacion': '2026-05-22',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Subactividad
        'viaje_aprobacion_tarea': {
            'path': 'correos/sistema/formularios/solicitudViaje/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'SV-202604-88CDE154',
                'monto': '1000.00',
                'fecha_aprobacion': '2026-04-26',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0027/ACT0003-CP-CD - Tarea',
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=26&tarea_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Actividad
        'viaje_rechazo_actividad': {
            'path': 'correos/sistema/formularios/solicitudViaje/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'SV-202605-D55229B7',
                'monto': '300.00',
                'fecha_rechazo': '2026-05-21',
                'motivo_rechazo': 'El evento no está contemplado en el POA del proyecto.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Subactividad
        'viaje_rechazo_tarea': {
            'path': 'correos/sistema/formularios/solicitudViaje/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'SV-202604-88CDE154',
                'monto': '1000.00',
                'fecha_rechazo': '2026-04-25',
                'motivo_rechazo': 'Falta especificar las instituciones participantes.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0027/ACT0003-CP-CD - Tarea',
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=26&tarea_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Actividad
        'viaje_nueva_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudViaje/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'SV-202605-D55229B7',
                'monto': '300.00',
                'fecha_correccion': '2026-05-23',
                'motivo_rechazo': 'El evento no está contemplado en el POA del proyecto.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Subactividad
        'viaje_nueva_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudViaje/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'SV-202604-88CDE154',
                'monto': '1000.00',
                'fecha_correccion': '2026-04-27',
                'motivo_rechazo': 'Falta especificar las instituciones participantes.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0027/ACT0003-CP-CD - Tarea',
                'accion_url': '/monitoreo/formulario055/89?solicitud_id=26&tarea_id=27',
                'accion_url_texto': 'Ir a la Solicitud de Viaje',
                'current_year': datetime.now().year,
            }
        },
        # ============================================================
        # SOLICITUD DE PAGO DIRECTO
        # ============================================================

        # Petición Revisión - Actividad
        'pago_directo_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SPD 00015',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '400.00',
                'fecha_solicitud': '2026-06-03',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=15',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },

        # Petición Revisión - Subactividad
        'pago_directo_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SPD 00016',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '600.00',
                'fecha_solicitud': '2026-06-03',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=16&tarea_id=26',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Actividad
        'pago_directo_aprobacion_actividad': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SPD 00015',
                'monto': '400.00',
                'fecha_aprobacion': '2026-06-05',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=15',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Subactividad
        'pago_directo_aprobacion_tarea': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SPD 00016',
                'monto': '600.00',
                'fecha_aprobacion': '2026-06-05',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=16&tarea_id=26',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Actividad
        'pago_directo_rechazo_actividad': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SPD 00015',
                'monto': '400.00',
                'fecha_rechazo': '2026-06-04',
                'motivo_rechazo': 'El proveedor no está registrado en el sistema.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=15',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Subactividad
        'pago_directo_rechazo_tarea': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'ACT0003-CP-CD - SPD 00016',
                'monto': '600.00',
                'fecha_rechazo': '2026-06-04',
                'motivo_rechazo': 'Falta adjuntar la factura correspondiente.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=16&tarea_id=26',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Actividad
        'pago_directo_nueva_revision_actividad': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'ACT0003-CP-CD - SPD 00015',
                'monto': '400.00',
                'fecha_correccion': '2026-06-06',
                'motivo_rechazo': 'El proveedor no está registrado en el sistema.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=15',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Subactividad
        'pago_directo_nueva_revision_tarea': {
            'path': 'correos/sistema/formularios/solicitudPagoDirecto/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'ACT0003-CP-CD - SPD 00016',
                'monto': '600.00',
                'fecha_correccion': '2026-06-06',
                'motivo_rechazo': 'Falta adjuntar la factura correspondiente.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario088/89?solicitud_id=16&tarea_id=26',
                'accion_url_texto': 'Ir al Pago Directo',
                'current_year': datetime.now().year,
            }
        },
        # ============================================================
        # RENDICIÓN DE CUENTAS
        # ============================================================

        # Petición Revisión - Actividad
        'rendicion_revision_actividad': {
            'path': 'correos/sistema/formularios/rendicionCuentas/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'FRC-12',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '1000.00',
                'fecha_solicitud': '2026-03-27',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=12',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },

        # Petición Revisión - Subactividad
        'rendicion_revision_tarea': {
            'path': 'correos/sistema/formularios/rendicionCuentas/peticion_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'FRC-13',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'monto': '5455.00',
                'fecha_solicitud': '2026-03-27',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=13&tarea_id=26',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Actividad
        'rendicion_aprobacion_actividad': {
            'path': 'correos/sistema/formularios/rendicionCuentas/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'FRC-12',
                'monto': '1000.00',
                'fecha_aprobacion': '2026-03-29',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=12',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },

        # Aprobación - Subactividad
        'rendicion_aprobacion_tarea': {
            'path': 'correos/sistema/formularios/rendicionCuentas/aprobacion.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_aprobador': 'Lic. Roberto Sánchez',
                'codigo': 'FRC-13',
                'monto': '5455.00',
                'fecha_aprobacion': '2026-03-29',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=13&tarea_id=26',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Actividad
        'rendicion_rechazo_actividad': {
            'path': 'correos/sistema/formularios/rendicionCuentas/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'FRC-12',
                'monto': '1000.00',
                'fecha_rechazo': '2026-03-28',
                'motivo_rechazo': 'Los comprobantes no coinciden con los montos declarados.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=12',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },

        # Rechazo - Subactividad
        'rendicion_rechazo_tarea': {
            'path': 'correos/sistema/formularios/rendicionCuentas/rechazo.html',
            'context': {
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'codigo': 'FRC-13',
                'monto': '5455.00',
                'fecha_rechazo': '2026-03-28',
                'motivo_rechazo': 'Falta el comprobante del servicio de catering.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=13&tarea_id=26',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Actividad
        'rendicion_nueva_revision_actividad': {
            'path': 'correos/sistema/formularios/rendicionCuentas/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'FRC-12',
                'monto': '1000.00',
                'fecha_correccion': '2026-03-30',
                'motivo_rechazo': 'Los comprobantes no coinciden con los montos declarados.',
                'subtipo_display': 'Actividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': None,
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=12',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },

        # Nueva Revisión - Subactividad
        'rendicion_nueva_revision_tarea': {
            'path': 'correos/sistema/formularios/rendicionCuentas/nueva_revision.html',
            'context': {
                'nombre_revisor': 'Lic. Roberto Sánchez',
                'solicitante_nombre': 'Alvaro Recoba Martines',
                'codigo': 'FRC-13',
                'monto': '5455.00',
                'fecha_correccion': '2026-03-30',
                'motivo_rechazo': 'Falta el comprobante del servicio de catering.',
                'subtipo_display': 'Subactividad',
                'actividad_nombre': 'Actividad Presupuesto',
                'tarea_nombre': 'SACT-0026/ACT0003-CP-CD - Descripcion',
                'accion_url': '/monitoreo/formulario022/89?solicitud_id=13&tarea_id=26',
                'accion_url_texto': 'Ir a la Rendición de Cuentas',
                'current_year': datetime.now().year,
            }
        },


        'test_estilos': {
            'path': 'correos/tests/test_estilos.html',
            'context': {
                'current_year': datetime.now().year,
                'app_url': 'http://localhost:5173',
                'support_url': 'http://localhost:5173/support',
                'privacy_url': 'http://localhost:5173/privacy',
                'referencia_id': 'TEST-2024-00001',
            }
        },
        'error': {
            'path': 'correos/sistema/preview_error.html',
            'context': {
                'error_message': 'Error inesperado del sistema.',
                'current_year': datetime.now().year,
            }
        },
    }
    
    def get_template_config(self, template_name):
        """
        Obtiene la configuración de un template por su nombre clave.
        
        Args:
            template_name (str): Nombre clave del template
            
        Returns:
            dict or None: Configuración del template
        """
        return self.TEMPLATES_CONFIG.get(template_name)
    
    def get_available_templates(self):
        """
        Retorna lista de templates disponibles con sus rutas.
        
        Returns:
            dict: Templates agrupados por directorio
        """
        available = {}
        for name, config in self.TEMPLATES_CONFIG.items():
            # Extraer categoría de la ruta
            path_parts = config['path'].split('/')
            # La categoría es: sistema/formularios/solicitudFondos
            if len(path_parts) >= 3:
                category = '/'.join(path_parts[1:-1])  # Excluye 'correos/' y el archivo
            else:
                category = 'general'
            
            if category not in available:
                available[category] = []
            
            available[category].append({
                'name': name,
                'path': config['path'],
            })
        
        return available
    
    def get(self, request, template_name=None):
        """
        Maneja la petición GET para previsualizar un template.
        """
        # Si no se especifica template, mostrar lista
        if template_name is None:
            return render(request, 'correos/sistema/preview_error.html', {
                'message': 'Selecciona un template para previsualizar.',
                'available': self.get_available_templates(),
            })
        
        # Buscar configuración del template
        config = self.get_template_config(template_name)
        
        if config is None:
            return render(request, 'correos/sistema/preview_error.html', {
                'message': f'Template "{template_name}" no encontrado.',
                'available': self.get_available_templates(),
            })
        
        # Renderizar template
        try:
            return render(
                request,
                config['path'],
                config['context']
            )
        except Exception as e:
            return render(request, 'correos/sistema/preview_error.html', {
                'message': f'Error al renderizar "{template_name}": {str(e)}',
                'template_path': config['path'],
                'available': self.get_available_templates(),
            })