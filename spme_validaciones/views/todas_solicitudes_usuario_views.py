# views/todas_solicitudes_usuario_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .solicitudes_fondos_usuario_views import SolicitudesFondosUsuarioView
from .solicitudes_viaje_usuario_views import SolicitudesViajeUsuarioView
from .solicitudes_pago_directo_usuario_views import SolicitudesPagoDirectoUsuarioView
from .solicitudes_reembolso_usuario_views import SolicitudesReembolsoUsuarioView
from .rendicion_cuentas_usuario_views import RendicionCuentasUsuarioView
from ..services.solicitudes_fondos_usuario_service import SolicitudesFondosUsuarioService
from ..services.solicitudes_viaje_usuario_service import SolicitudesViajeUsuarioService
from ..services.solicitudes_pago_directo_usuario_service import SolicitudesPagoDirectoUsuarioService
from ..services.solicitudes_reembolso_usuario_service import SolicitudesReembolsoUsuarioService
from ..services.rendicion_cuentas_usuario_service import RendicionCuentasUsuarioService


class TodasSolicitudesUsuarioView(APIView):
    """
    Endpoint maestro que consolida todos los tipos de solicitudes.
    
    GET /api-valid/todas-mis-solicitudes/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        usuario_id = request.user.id
        
        # Servicios para pendientes
        servicio_fondos = SolicitudesFondosUsuarioService()
        servicio_viajes = SolicitudesViajeUsuarioService()
        servicio_pagos = SolicitudesPagoDirectoUsuarioService()
        servicio_reembolsos = SolicitudesReembolsoUsuarioService()
        servicio_rendiciones = RendicionCuentasUsuarioService()
        
        # Obtener todas las solicitudes
        fondos = SolicitudesFondosUsuarioView.as_service(usuario_id)
        viajes = SolicitudesViajeUsuarioView.as_service(usuario_id)
        pagos = SolicitudesPagoDirectoUsuarioView.as_service(usuario_id)
        reembolsos = SolicitudesReembolsoUsuarioView.as_service(usuario_id)
        rendiciones = RendicionCuentasUsuarioView.as_service(usuario_id)
        
        # Obtener pendientes
        pendientes_fondos = servicio_fondos.obtener_pendientes_revision(usuario_id)
        pendientes_viajes = servicio_viajes.obtener_pendientes_revision(usuario_id)
        pendientes_pagos = servicio_pagos.obtener_pendientes_revision(usuario_id)
        pendientes_reembolsos = servicio_reembolsos.obtener_pendientes_revision(usuario_id)
        pendientes_rendiciones = servicio_rendiciones.obtener_pendientes_revision(usuario_id)
        
        total_pendientes = (
            len(pendientes_fondos) + 
            len(pendientes_viajes) + 
            len(pendientes_pagos) + 
            len(pendientes_reembolsos) + 
            len(pendientes_rendiciones)
        )
        
        return Response({
            'solicitudesFondos': fondos,
            'solicitudesViaje': viajes,
            'solicitudesPagoDirecto': pagos,
            'solicitudesReembolso': reembolsos,
            'rendicionesCuentas': rendiciones,
            'pendientesRevision': {
                'totalPendientes': total_pendientes,
                'solicitudesFondos': pendientes_fondos,
                'solicitudesViaje': pendientes_viajes,
                'solicitudesPagoDirecto': pendientes_pagos,
                'solicitudesReembolso': pendientes_reembolsos,
                'rendicionesCuentas': pendientes_rendiciones,
            }
        })