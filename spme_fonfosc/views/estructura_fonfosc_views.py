from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import ProyectoFonFosc
from ..serializers.estructura_fonfosc_serializers import ProyectoFonFoscSerializer

class ProyectoFonFoscViewSet(viewsets.ModelViewSet):
    queryset = ProyectoFonFosc.objects.all()
    serializer_class = ProyectoFonFoscSerializer
    # permission_classes = [IsAuthenticated]
    
    # Endpoint para obtener estructura completa del proyecto
    @action(detail=True, methods=['get'], url_path='estructura-completa')
    def estructura_completa(self, request, pk=None):
        """
        Obtiene la estructura completa de un proyecto FONFOSC:
        - Proyecto
          - Institución
          - Objetivo
            - Indicadores del objetivo
            - Resultados
              - Indicadores del resultado
        """
        try:
            # Obtener el proyecto con todas las relaciones usando select_related y prefetch_related
            proyecto = get_object_or_404(
                ProyectoFonFosc.objects.select_related(
                    'institucion',
                    'responsable',
                    'pei',
                    'objetivo_general_fonfosc'
                ).prefetch_related(
                    'procedencia_fondos',
                    'objetivo_general_fonfosc__resultados_fonfosc',
                    'objetivo_general_fonfosc__resultados_fonfosc__indicador_resultado_fonfosc',
                    'objetivo_general_fonfosc__indicador_objetivo_fonfosc'
                ),
                pk=pk
            )
            
            # Estructurar la respuesta según el formato solicitado
            estructura = {
                'proyecto': {
                    'id': proyecto.id,
                    'codigo': proyecto.codigo,
                    'titulo': proyecto.titulo,
                    'descripcion': proyecto.descripcion,
                    'estado': proyecto.get_estado_display() if hasattr(proyecto, 'get_estado_display') else proyecto.estado,
                    'categoria': proyecto.get_categoria_display() if hasattr(proyecto, 'get_categoria_display') else proyecto.categoria,
                    'presupuesto': str(proyecto.presupuesto) if proyecto.presupuesto else None,
                    'fechas': {
                        'creacion': proyecto.fecha_creacion,
                        'inicio': proyecto.fecha_inicio,
                        'finalizacion': proyecto.fecha_finalizacion
                    },
                    'cobertura_geografica': proyecto.cobertura_geografica,
                    'institucion': {
                        'id': proyecto.institucion.id if proyecto.institucion else None,
                        'sigla': proyecto.institucion.sigla if proyecto.institucion else None,
                        'nombre': proyecto.institucion.nombre if proyecto.institucion else None,
                        'email': proyecto.institucion.emailInstitucion if proyecto.institucion else None,
                        'telefono': proyecto.institucion.telefono if proyecto.institucion else None
                    } if proyecto.institucion else None,
                    'responsable': {
                        'id': proyecto.responsable.id if proyecto.responsable else None,
                        'username': proyecto.responsable.username if proyecto.responsable else None,
                        'nombre_completo': proyecto.responsable.get_full_name() if proyecto.responsable else None,
                        'nombre': proyecto.responsable.nombre if proyecto.responsable else None,
                        'paterno': proyecto.responsable.paterno if proyecto.responsable else None,
                        'materno': proyecto.responsable.materno if proyecto.responsable else None,
                        'correo': proyecto.responsable.correo if proyecto.responsable else None,
                        'ci': proyecto.responsable.ci if proyecto.responsable else None,
                        'cargo': proyecto.responsable.cargo if proyecto.responsable else None
                    } if proyecto.responsable else None,
                    'pei': {
                        'id': proyecto.pei.id if proyecto.pei else None,
                        'titulo': proyecto.pei.titulo if proyecto.pei else None
                    } if proyecto.pei else None,
                    'procedencia_fondos': [
                        {
                            'id': pf.id,
                            'nombre': pf.nombre if hasattr(pf, 'nombre') else str(pf)
                        } for pf in proyecto.procedencia_fondos.all()
                    ],
                    'objetivo': None
                }
            }
            
            # Agregar objetivo si existe
            if hasattr(proyecto, 'objetivo_general_fonfosc') and proyecto.objetivo_general_fonfosc:
                objetivo = proyecto.objetivo_general_fonfosc
                estructura['proyecto']['objetivo'] = {
                    'id': objetivo.id,
                    'codigo': objetivo.codigo,
                    'redaccion': objetivo.redaccion,
                    'supuestosRiesgos': objetivo.supuestosRiesgos,
                    'indicadores_objetivo': [
                        {
                            'id': io.id,
                            'codigo': io.codigo,
                            'descripcion': io.descripcion,
                            'tipo': io.get_tipo_display() if hasattr(io, 'get_tipo_display') else io.tipo,
                            'frecuencia': io.get_frecuencia_display() if hasattr(io, 'get_frecuencia_display') else io.frecuencia,
                            'baseline': io.baseline,
                            'target_q1': io.target_q1,
                            'target_q2': io.target_q2,
                            'target_q3': io.target_q3,
                            'target_q4': io.target_q4,
                            'fechas_target': {
                                'linea_base': io.fechaLineaBase,
                                'target_poblacion': io.fechaTargetPoblacion,
                                'target_q1': io.fechaTargetQ1,
                                'target_q2': io.fechaTargetQ2,
                                'target_q3': io.fechaTargetQ3,
                                'target_q4': io.fechaTargetQ4
                            }
                        } for io in objetivo.indicador_objetivo_fonfosc.all()
                    ],
                    'resultados': [
                        {
                            'id': resultado.id,
                            'codigo': resultado.codigo,
                            'descripcion': resultado.descripcion,
                            'supuestosRiesgos': resultado.supuestosRiesgos,
                            'indicadores_resultado': [
                                {
                                    'id': ir.id,
                                    'codigo': ir.codigo,
                                    'descripcion': ir.descripcion,
                                    'tipo': ir.get_tipo_display() if hasattr(ir, 'get_tipo_display') else ir.tipo,
                                    'frecuencia': ir.get_frecuencia_display() if hasattr(ir, 'get_frecuencia_display') else ir.frecuencia,
                                    'baseline': ir.baseline,
                                    'target_q1': ir.target_q1,
                                    'target_q2': ir.target_q2,
                                    'target_q3': ir.target_q3,
                                    'target_q4': ir.target_q4,
                                    'fechas_target': {
                                        'linea_base': ir.fechaLineaBase,
                                        'target_poblacion': ir.fechaTargetPoblacion,
                                        'target_q1': ir.fechaTargetQ1,
                                        'target_q2': ir.fechaTargetQ2,
                                        'target_q3': ir.fechaTargetQ3,
                                        'target_q4': ir.fechaTargetQ4
                                    }
                                } for ir in resultado.indicador_resultado_fonfosc.all()
                            ]
                        } for resultado in objetivo.resultados_fonfosc.all()
                    ]
                }
            
            return Response({
                'success': True,
                'data': estructura,
                'message': 'Estructura del proyecto obtenida correctamente'
            }, status=status.HTTP_200_OK)
            
        except ProyectoFonFosc.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Proyecto no encontrado',
                'message': f'No se encontró un proyecto con ID {pk}'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al obtener la estructura del proyecto'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        