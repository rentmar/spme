# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import json
from spme_estructuracion_pei.models import ActividadPei
from ..serializers.actualizar_actividades_pei_bulk_serializer import ActividadPeiBatchUpdateSerializer

@api_view(['POST'])
def actualizar_multiples_actividades(request):
    """
    Endpoint para actualizar múltiples actividades en lote.
    
    POST /api/actividades/actualizar-lote/
    
    Request Body:
    [
        {
            "id": 1,
            "codigo": "ACT-PEI-2024-001",
            "nombreCorto": "Capacitación en Gestión de Proyectos",
            "descripcion": "Capacitación para el equipo...",
            "supuestos": "Disponibilidad de participantes...",
            "riesgos": "Posible cancelación...",
            "estado": "CRD",
            "tipo": "No definido",
            "fecha_inicio": "2024-01-15",
            "fecha_cierre": "2024-01-20",
            "procedencia_fondos": {
                "fuente_principal": "Presupuesto interno operativo",
                "fuente_secundaria": "Fondos de cooperación externa",
                "monto_fuente1": "3000.00",
                "monto_fuente2": "2000.00"
            },
            "presupuesto": "5000.00",
            "responsable_username": "admin",
            "responsable_id": 1,
            "gradoEjecucion": ""
        },
        ...
    ]
    
    Response:
    {
        "success": true,
        "message": "3 actividades actualizadas correctamente",
        "results": [
            {
                "id": 1,
                "codigo": "ACT-PEI-2024-001",
                "status": "updated",
                "errors": null
            },
            ...
        ],
        "total_actualizadas": 3,
        "total_errores": 0
    }
    """
    
    if not isinstance(request.data, list):
        return Response(
            {"error": "El body debe ser un array de actividades"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    actividades_data = request.data
    results = []
    total_actualizadas = 0
    total_errores = 0
    
    try:
        with transaction.atomic():
            for index, actividad_data in enumerate(actividades_data):
                try:
                    # Validar que el ID existe
                    if 'id' not in actividad_data:
                        raise ValidationError(f"Actividad en posición {index} no tiene ID")
                    
                    actividad_id = actividad_data['id']
                    
                    # Obtener la actividad o retornar error
                    try:
                        actividad = ActividadPei.objects.get(id=actividad_id)
                    except ActividadPei.DoesNotExist:
                        results.append({
                            "id": actividad_id,
                            "codigo": actividad_data.get('codigo', ''),
                            "status": "error",
                            "errors": f"Actividad con ID {actividad_id} no encontrada"
                        })
                        total_errores += 1
                        continue
                    
                    # Crear instancia del serializer
                    serializer = ActividadPeiBatchUpdateSerializer(
                        instance=actividad,
                        data=actividad_data,
                        partial=True
                    )
                    
                    if serializer.is_valid():
                        # Guardar la actividad
                        actividad_actualizada = serializer.save()
                        
                        results.append({
                            "id": actividad_id,
                            "codigo": actividad_actualizada.codigo,
                            "status": "updated",
                            "errors": None
                        })
                        total_actualizadas += 1
                        
                    else:
                        results.append({
                            "id": actividad_id,
                            "codigo": actividad_data.get('codigo', ''),
                            "status": "error",
                            "errors": serializer.errors
                        })
                        total_errores += 1
                        
                except Exception as e:
                    results.append({
                        "id": actividad_data.get('id', f'index_{index}'),
                        "codigo": actividad_data.get('codigo', ''),
                        "status": "error",
                        "errors": str(e)
                    })
                    total_errores += 1
            
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": f"Error en la transacción: {str(e)}",
                "total_actualizadas": total_actualizadas,
                "total_errores": total_errores
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response(
        {
            "success": True,
            "message": f"{total_actualizadas} actividades actualizadas correctamente",
            "results": results,
            "total_actualizadas": total_actualizadas,
            "total_errores": total_errores
        },
        status=status.HTTP_200_OK
    )