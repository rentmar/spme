# views.py
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from spme_estructuracion_pei.models import (
    Pei, 
    ObjetivoPei, 
    ActividadPei, 
    TareaActividadPei,
    IndicadorPeiCualitativo,
    IndicadorPeiCuantitativo,
    FactoresCriticos,
    )

class PeiDashboardEstructuraSimpleView(APIView):
    """
    Dashboard con estructura simple del PEI
    """
    # permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            pei = Pei.objects.get(pk=pk)
        except Pei.DoesNotExist:
            return Response(
                {'error': 'PEI no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        objetivos = pei.pei_obj_general.all()
        actividades = pei.actividad_pei.all()
        tareas = TareaActividadPei.objects.filter(actividad__pei=pei)
        
        # Estructura simple sin problemas de polimorfismo
        estructura = []
        for objetivo in objetivos:
            indicadores = objetivo.indicador_pei_objetivo.count()
            factores = objetivo.factores_criticos.count()
            
            estructura.append({
                'objetivo_id': objetivo.id,
                'objetivo_codigo': objetivo.codigo or f"OBJ-{objetivo.id}",
                'descripcion': objetivo.descripcion[:150] + '...' if objetivo.descripcion and len(objetivo.descripcion) > 150 else objetivo.descripcion,
                'factores_criticos': factores,
                'indicadores': indicadores,
                'actividades_relacionadas': objetivo.actividades_relacionadas.count(),
            })
        
        # Datos básicos
        hoy = timezone.now().date()
        vigencia = 'NO DEFINIDA'
        if pei.fecha_inicio and pei.fecha_fin:
            if pei.fecha_inicio <= hoy <= pei.fecha_fin:
                vigencia = 'VIGENTE'
            elif hoy < pei.fecha_inicio:
                vigencia = 'PENDIENTE'
            else:
                vigencia = 'VENCIDO'
        
        # Financiero
        presupuesto_total = actividades.aggregate(total=Sum('presupuesto'))['total'] or 0
        ejecutado_total = actividades.aggregate(total=Sum('totalEjecutado'))['total'] or 0
        
        data = {
            'pei': {
                'id': pei.id,
                'titulo': pei.titulo,
                'descripcion': pei.descripcion,
                'vigencia': vigencia,
                'fecha_inicio': pei.fecha_inicio,
                'fecha_fin': pei.fecha_fin,
            },
            
            'resumen': {
                'objetivos': objetivos.count(),
                'factores_criticos': sum(obj.factores_criticos.count() for obj in objetivos),
                'indicadores': sum(obj.indicador_pei_objetivo.count() for obj in objetivos),
                'actividades': actividades.count(),
                'tareas': tareas.count(),
            },
            
            'financiero': {
                'presupuesto': float(presupuesto_total),
                'ejecutado': float(ejecutado_total),
                'saldo': float(presupuesto_total - ejecutado_total),
                'porcentaje': round((ejecutado_total / presupuesto_total * 100), 1) if presupuesto_total > 0 else 0,
            },
            
            'estructura': estructura,
            
            'estado_actividades': {
                'creadas': actividades.filter(estado='CRD').count(),
                'planificadas': actividades.filter(estado='PLAN').count(),
                'ejecucion': actividades.filter(estado='EJEC').count(),
                'finalizadas': actividades.filter(estado='FIN').count(),
                'retrasadas': actividades.filter(estado='RETR').count(),
            }
        }
        
        return Response(data)