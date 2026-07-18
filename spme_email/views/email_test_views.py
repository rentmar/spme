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
        # Aquí agregarás más templates:
        # 'solicitud_pago_directo': {
        #     'path': 'correos/sistema/formularios/solicitudPagoDirecto/...',
        #     'context': { ... }
        # },
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