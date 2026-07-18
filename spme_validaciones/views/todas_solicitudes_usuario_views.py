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

        #Obtener solicitudes donde es revisor
        revisor_fondos = servicio_fondos.obtener_validaciones_como_validador(usuario_id)
        revisor_viajes = servicio_viajes.obtener_validaciones_como_validador(usuario_id)
        revisor_pagos = servicio_pagos.obtener_validaciones_como_validador(usuario_id)
        revisor_reembolsos = servicio_reembolsos.obtener_validaciones_como_validador(usuario_id)
        revisor_rendiciones = servicio_rendiciones.obtener_validaciones_como_validador(usuario_id)

        total_revisiones = (
            len(revisor_fondos) +
            len(revisor_viajes) +
            len(revisor_pagos) +
            len(revisor_reembolsos) +
            len(revisor_rendiciones) 
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
            },
            'solicitudesRevisor':{
                'totalRevisiones': total_revisiones,
                'solicitudesFondos': revisor_fondos,
                'solicitudesViaje': revisor_viajes,
                'solicitudesPagoDirecto': revisor_pagos,
                'solicitudesReembolso': revisor_reembolsos,
                'rendicionesCuentas': revisor_rendiciones,
            }
        })
    

class TodasSolicitudesPendientesUsuarioView(APIView):
    """
    Endpoint para obtener todas las solicitudes pendientes para revision de un usuario
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario_id = request.user.id

        #Servicios para pendientes
        servicio_fondos = SolicitudesFondosUsuarioService()
        servicio_viajes = SolicitudesViajeUsuarioService()
        servicio_pagos = SolicitudesPagoDirectoUsuarioService()
        servicio_reembolsos = SolicitudesReembolsoUsuarioService()
        servicio_rendiciones = RendicionCuentasUsuarioService()

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
            'pendientesRevision': {
                'totalPendientes': total_pendientes,
                'solicitudesFondos': pendientes_fondos,
                'solicitudesViaje': pendientes_viajes,
                'solicitudesPagoDirecto': pendientes_pagos,
                'solicitudesReembolso': pendientes_reembolsos,
                'rendicionesCuentas': pendientes_rendiciones,
            }
        })
    

class TodasValidacionesUsuarioView(APIView):
    """
    Endpoint para obtener TODAS las validaciones donde el usuario es validador.
    
    GET /api-valid/mis-validaciones/
    
    Incluye todos los estados: PENDIENTE, APROBADO, RECHAZADO
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario_id = request.user.id

        servicio_fondos = SolicitudesFondosUsuarioService()
        servicio_viajes = SolicitudesViajeUsuarioService()
        servicio_pagos = SolicitudesPagoDirectoUsuarioService()
        servicio_reembolsos = SolicitudesReembolsoUsuarioService()
        servicio_rendiciones = RendicionCuentasUsuarioService()

        # Obtener todas las validaciones (no solo pendientes)

        fondos = servicio_fondos.obtener_validaciones_como_validador(usuario_id)
        viajes = servicio_viajes.obtener_validaciones_como_validador(usuario_id)
        pagos = servicio_pagos.obtener_validaciones_como_validador(usuario_id)
        reembolsos = servicio_reembolsos.obtener_validaciones_como_validador(usuario_id)
        rendiciones = servicio_rendiciones.obtener_validaciones_como_validador(usuario_id)

        todas = fondos + viajes + pagos + reembolsos + rendiciones

        return Response({
            'total': len(todas),
            'solicitudesFondos': fondos,
            'solicitudesViaje': viajes,
            'solicitudesPagoDirecto': pagos,
            'solicitudesReembolso': reembolsos,
            'rendicionesCuentas': rendiciones,
            'resumen': {
                'total': len(todas),
                'pendientes': sum(1 for v in todas if v['estado'] == 'PENDIENTE'),
                'aprobadas': sum(1 for v in todas if v['estado'] == 'APROBADO'),
                'rechazadas': sum(1 for v in todas if v['estado'] == 'RECHAZADO'),
                'fondos': len(fondos),
                'viajes': len(viajes),
                'pagosDirectos': len(pagos),
                'reembolsos': len(reembolsos),
                'rendicionesCuentas': len(rendiciones),
            }
        })

