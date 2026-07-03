from .base_repository import BaseValidacionRepository
from ..models import ValidacionRendicionCuentas
from django.utils import timezone
from datetime import timedelta

class ValidacionRendicionCuentasRepository(BaseValidacionRepository):
    """
    Repositorio para ValidacionRendicionCuentas.
    """
    def __init__(self):
        super().__init__(ValidacionRendicionCuentas)

    def obtener_por_rendicion(self, rendicion_id):
        return self.obtener_por_documento(
            documento_id=rendicion_id,
            campo_fk='rendicion',
            select_related=['usuarioValidador', 'usuarioRedactor', 'rendicion']
        )
    
    def obtener_pendientes_por_rendicion(self, rendicion_id):
        return self.obtener_pendientes_por_documento(
            documento_id=rendicion_id,
            campo_fk='rendicion',
            select_related=['usuarioValidador']
        )
    
    def obtener_resumen_estado_rendicion(self, rendicion_id):
        return self.obtener_resumen_estado(
            documento_id=rendicion_id,
            campo_fk='rendicion'
        )

    def obtener_estadisticas_por_rendicion(self, rendicion_id):
        validaciones = self.obtener_por_rendicion(rendicion_id)
        total = validaciones.count()
        
        if total == 0:
            return {
                'total': 0,
                'estado_consolidado': 'SIN_VALIDACIONES',
                'resumen': None,
                'detalle_validadores': []
            }
        
        resumen = self.obtener_resumen_estado_rendicion(rendicion_id)
        
        if resumen['rechazado']:
            estado_consolidado = 'RECHAZADO'
        elif resumen['pendientes'] > 0:
            estado_consolidado = 'PENDIENTE'
        elif resumen['aprobado_totalmente']:
            estado_consolidado = 'APROBADO'
        else:
            estado_consolidado = 'PARCIAL'
        
        detalle = []
        for v in validaciones:
            redactor = v.usuarioRedactor
            detalle.append({
                'validacion_id': v.id,
                'validador_id': v.usuarioValidador_id,
                'validador_nombre': v.usuarioValidador.get_full_name(),
                'estado': v.estado,
                'comentarios': v.comentarios,
                'fecha_asignacion': v.fechaAsignacion,
                'fecha_resolucion': v.fechaResolucion,
                'codigo_seguimiento': v.codigoSeguimiento,
                'version_documento': v.versionDocumento,
                'redactor': {
                    'id': redactor.id,
                    'nombre_completo': redactor.get_full_name(),
                    'email': redactor.correo if hasattr(redactor, 'correo') else getattr(redactor, 'email', ''),
                    'rol': redactor.cargo if hasattr(redactor, 'cargo') else '',
                    'username': redactor.username
                }
            })
        
        return {
            'total': total,
            'estado_consolidado': estado_consolidado,
            'resumen': resumen,
            'detalle_validadores': detalle
        }
    
    def obtener_por_validador_con_rendicion(self, usuario_id):
        return self.model_class.objects.filter(
            usuarioValidador_id=usuario_id
        ).select_related(
            'rendicion', 'rendicion__usuario', 'usuarioRedactor'
        ).order_by('-fechaAsignacion')
    
    def obtener_por_redactor(self, usuario_id):
        return self.model_class.objects.filter(
            usuarioRedactor_id=usuario_id
        ).select_related(
            'rendicion', 'usuarioValidador'
        ).order_by('-fechaAsignacion')
    
    def obtener_pendientes_urgentes(self, usuario_id, horas=24):
        limite = timezone.now() - timedelta(hours=horas)
        return self.model_class.objects.filter(
            usuarioValidador_id=usuario_id,
            estado='PENDIENTE',
            fechaAsignacion__lte=limite
        ).select_related('rendicion').order_by('fechaAsignacion')