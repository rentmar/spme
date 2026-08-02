# spme_impresiones/validadores_documentos_service.py

from django.apps import apps
from typing import List, Dict, Optional, Any


class ValidadoresDocumentoService:
    """
    Servicio para extraer validadores de documentos y preparar contexto para PDFs.
    
    Uso:
        service = ValidadoresDocumentoService()
        
        # Obtener solo validadores
        validadores = service.obtener_validadores(solicitud)
        
        # Obtener contexto completo para PDF
        contexto = service.preparar_contexto_pdf(solicitud)
    """
    
    # ------------------------------------------------------------------
    # MAPEO DE DOCUMENTOS A MODELOS DE VALIDACIÓN
    # ------------------------------------------------------------------
    MAPEO_DOCUMENTO_VALIDACION = {
        'SolicitudFondos': 'ValidacionSolicitudFondos',
        'SolicitudViaje': 'ValidacionSolicitudViaje',
        'SolicitudPagoDirecto': 'ValidacionSolicitudPagoDirecto',
        'SolicitudReembolso': 'ValidacionSolicitudReembolso',
        'RendicionCuentas': 'ValidacionRendicionCuentas',
    }
    
    # ------------------------------------------------------------------
    # MAPEO DE CARGOS A ETIQUETAS
    # ------------------------------------------------------------------
    MAPEO_CARGOS = {
        'admin': 'Administrador',
        'coordinador': 'Coordinador',
        'tecnico': 'Técnico',
        'contable': 'Contable',
        'dir-administrativo': 'Director Administrativo',
        None: 'Revisor',
        '': 'Revisor',
    }
    
    # ------------------------------------------------------------------
    # ESTADOS
    # ------------------------------------------------------------------
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_APROBADO = 'APROBADO'
    ESTADO_RECHAZADO = 'RECHAZADO'
    ESTADO_SIN_REVISORES = 'SIN_REVISORES'
    
    # ------------------------------------------------------------------
    # MÉTODOS PRIVADOS
    # ------------------------------------------------------------------
    
    def _get_validacion_model(self, documento: Any):
        """
        Obtiene la clase del modelo de validación según el tipo de documento.
        
        Args:
            documento: Instancia de un documento (SolicitudFondos, RendicionCuentas, etc.)
            
        Returns:
            Clase del modelo de validación
            
        Raises:
            ValueError: Si no hay mapeo para el tipo de documento
        """
        nombre_modelo = documento.__class__.__name__
        
        if nombre_modelo not in self.MAPEO_DOCUMENTO_VALIDACION:
            raise ValueError(
                f"No existe mapeo de validación para '{nombre_modelo}'. "
                f"Documentos soportados: {list(self.MAPEO_DOCUMENTO_VALIDACION.keys())}"
            )
        
        nombre_validacion = self.MAPEO_DOCUMENTO_VALIDACION[nombre_modelo]
        
        try:
            return apps.get_model('spme_validaciones', nombre_validacion)
        except LookupError:
            raise ValueError(
                f"No se encontró el modelo '{nombre_validacion}' "
                f"para el documento '{nombre_modelo}'"
            )
    
    def _get_campo_documento(self, validacion_model: Any) -> str:
        """
        Determina el nombre del campo ForeignKey que relaciona 
        la validación con el documento.
        """
        nombre_validacion = validacion_model.__name__
        
        if 'Solicitud' in nombre_validacion:
            return 'solicitud'
        elif nombre_validacion == 'ValidacionRendicionCuentas':
            return 'rendicion'
        elif nombre_validacion == 'ValidacionInformeActividad':
            return 'informe'
        elif nombre_validacion == 'ValidacionInformeTarea':
            return 'informeTarea'
        else:
            raise ValueError(f"No se puede determinar el campo para '{nombre_validacion}'")
    
    def _get_etiqueta_cargo(self, cargo: Optional[str], mapeo_personalizado: Optional[Dict[str, str]] = None) -> str:
        """
        Obtiene la etiqueta legible para un cargo.
        
        Args:
            cargo: Cargo del usuario (admin, coordinador, etc.)
            mapeo_personalizado: Diccionario opcional para sobrescribir etiquetas
            
        Returns:
            Etiqueta legible del cargo
        """
        mapeo = {**self.MAPEO_CARGOS}
        if mapeo_personalizado:
            mapeo.update(mapeo_personalizado)
        
        return mapeo.get(cargo, mapeo.get(None, 'Revisor'))
    
    # ------------------------------------------------------------------
    # MÉTODOS PÚBLICOS
    # ------------------------------------------------------------------
    
    def obtener_validadores(
        self, 
        documento: Any, 
        etiquetas_personalizadas: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los validadores de un documento.
        
        Args:
            documento: Instancia del documento
            etiquetas_personalizadas: Diccionario opcional para personalizar etiquetas
            Ej: {'contable': 'Contador Asignado'}
            
        Returns:
            Lista de diccionarios:
            [
                {
                    'rol': 'REVISOR 1',
                    'etiqueta_cargo': 'Contable',
                    'nombre': 'Juan Pérez',
                    'cargo': 'contable',
                    'estado': 'APROBADO',
                    'estado_display': 'Aprobado',
                    'fecha_resolucion': '01/01/2026',
                    'comentarios': 'Todo correcto',
                    'codigo_seguimiento': 'SF-20260101-ABC12345'
                },
                ...
            ]
        """
        # 1. Obtener modelo de validación
        validacion_model = self._get_validacion_model(documento)
        
        # 2. Determinar campo de relación
        campo = self._get_campo_documento(validacion_model)
        
        # 3. Construir filtro y consultar
        filtro = {campo: documento}
        validaciones = validacion_model.objects.filter(**filtro).order_by('fechaAsignacion')
        
        # 4. Construir lista de validadores
        validadores = []
        for i, validacion in enumerate(validaciones, 1):
            validador = validacion.usuarioValidador
            cargo = validador.cargo if validador else None
            etiqueta = self._get_etiqueta_cargo(cargo, etiquetas_personalizadas)
            
            validadores.append({
                'rol': f'REVISOR {i}',
                'etiqueta_cargo': etiqueta,
                'nombre': validador.get_full_name() if validador else 'No asignado',
                'cargo': cargo or 'No especificado',
                'estado': validacion.estado,
                'estado_display': validacion.get_estado_display(),
                'fecha_resolucion': (
                    validacion.fechaResolucion.strftime('%d/%m/%Y') 
                    if validacion.fechaResolucion 
                    else None
                ),
                'comentarios': validacion.comentarios or '',
                'codigo_seguimiento': validacion.codigoSeguimiento,
            })
        
        return validadores
    
    def obtener_solicitante(self, documento: Any) -> Dict[str, Any]:
        """
        Obtiene los datos del solicitante (redactor) del documento.
        
        Args:
            documento: Instancia del documento
            
        Returns:
            Diccionario con datos del solicitante
        """
        usuario = documento.usuario if hasattr(documento, 'usuario') and documento.usuario else None
        
        if not usuario:
            return {
                'rol': 'SOLICITANTE',
                'nombre': 'No asignado',
                'cargo': 'No especificado',
                'documento_identidad': 'No asignado',
            }
        
        return {
            'rol': 'SOLICITANTE',
            'nombre': usuario.get_full_name(),
            'cargo': usuario.cargo or 'No especificado',
            'documento_identidad': usuario.ci or 'No asignado',
        }
    
    def calcular_estado_documento(self, validadores: List[Dict[str, Any]]) -> str:
        """
        Calcula el estado global del documento.
        
        Reglas:
        - SIN_REVISORES: No hay validadores
        - RECHAZADO: Al menos uno rechazó
        - PENDIENTE: Al menos uno está pendiente
        - APROBADO: Todos aprobaron
        
        Args:
            validadores: Lista de validadores
            
        Returns:
            'SIN_REVISORES' | 'PENDIENTE' | 'APROBADO' | 'RECHAZADO'
        """
        if not validadores:
            return self.ESTADO_SIN_REVISORES
        
        estados = [v['estado'] for v in validadores]
        
        if self.ESTADO_RECHAZADO in estados:
            return self.ESTADO_RECHAZADO
        
        if self.ESTADO_PENDIENTE in estados:
            return self.ESTADO_PENDIENTE
        
        if all(e == self.ESTADO_APROBADO for e in estados):
            return self.ESTADO_APROBADO
        
        return self.ESTADO_PENDIENTE
    
    def preparar_contexto_pdf(self, documento: Any) -> Dict[str, Any]:
        """
        Prepara el contexto completo de validaciones para inyectar en el PDF.
        
        Args:
            documento: Instancia del documento
            
        Returns:
            Diccionario listo para incluir en el contexto:
            {
                'validadores': [...],
                'solicitante': {...},
                'estado_documento': 'PENDIENTE',
                'total_validadores': 2,
                'aprobados': 1,
                'pendientes': 1,
                'rechazados': 0,
            }
        """
        validadores = self.obtener_validadores(documento)
        solicitante = self.obtener_solicitante(documento)
        estado = self.calcular_estado_documento(validadores)
        
        conteo = {
            'total_validadores': len(validadores),
            'aprobados': sum(1 for v in validadores if v['estado'] == self.ESTADO_APROBADO),
            'pendientes': sum(1 for v in validadores if v['estado'] == self.ESTADO_PENDIENTE),
            'rechazados': sum(1 for v in validadores if v['estado'] == self.ESTADO_RECHAZADO),
        }
        
        return {
            'validadores': validadores,
            'solicitante': solicitante,
            'estado_documento': estado,
            **conteo,
        }