# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Max, Q
from ..serializers.planificacion_pei_bulk_serializer import (
    ProcesarActividadesSimpleSerializer,
    ActividadSimpleSerializer
)

from ..models import PlanificacionPei
from spme_estructuracion_pei.models import ActividadPei, Pei
from spme_autenticacion.models import Usuario
from spme_actividades.models import TipoActividad

class ProcesarPlanificacionPeiView(APIView):
    """
    Endpoint simplificado para procesar actividades y crear registro de planificación PEI.
    """
    # permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Procesa actividades y crea registro de seguimiento.
        """
        # Validar datos básicos
        serializer = ProcesarActividadesSimpleSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'Datos inválidos',
                    'detalles': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        
        try:
            # Usar transacción atómica
            with transaction.atomic():
                return self._procesar_transaccion_simple(validated_data, request.user)
                
        except Exception as e:
            return self._handle_error(e)
    
    def _procesar_transaccion_simple(self, validated_data, usuario):
        """
        Procesa la transacción completa.
        """
        # 1. Procesar actividades
        actividades_resultados = self._procesar_actividades_simple(
            validated_data['actividades'], 
            usuario
        )
        
        # 2. Verificar que hubo al menos una actividad exitosa
        if not actividades_resultados['actividades_procesadas']:
            raise ValueError("No se pudo procesar ninguna actividad")
        
        # 3. Crear registro de planificación
        planificacion = self._crear_planificacion_simple(
            validated_data['seguimiento'], 
            usuario,
            actividades_resultados['actividades_procesadas']
        )
        
        # 4. Preparar respuesta
        return self._build_success_response_simple(
            planificacion, 
            actividades_resultados
        )
    
    def _procesar_actividades_simple(self, actividades_data, usuario):
        """
        Procesa cada actividad de forma simplificada.
        """
        total_actividades = len(actividades_data)
        creadas = 0
        actualizadas = 0
        fallidas = []
        actividades_procesadas = []
        
        for actividad_data in actividades_data:
            try:
                actividad, created = self._procesar_actividad_simple(
                    actividad_data, 
                    usuario
                )
                
                if created:
                    creadas += 1
                else:
                    actualizadas += 1
                
                actividades_procesadas.append(actividad)
                
            except Exception as e:
                # Si una actividad falla, la registramos y seguimos
                fallidas.append({
                    'codigo': actividad_data.get('codigo', 'Sin código'),
                    'id': actividad_data.get('id', 'Sin ID'),
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                })
                # IMPORTANTE: Si quieres rollback total, descomenta:
                # raise e
        
        return {
            'total': total_actividades,
            'creadas': creadas,
            'actualizadas': actualizadas,
            'fallidas': fallidas,
            'actividades_procesadas': actividades_procesadas
        }
    
    def _procesar_actividad_simple(self, actividad_data, usuario):
        """
        Procesa una actividad individual de forma simplificada.
        """
        # 1. Validar datos mínimos
        if 'codigo' not in actividad_data:
            raise ValueError("La actividad debe tener un código")
        
        if 'pei' not in actividad_data:
            raise ValueError("La actividad debe tener un PEI asociado")
        
        # 2. Preparar datos para la actividad
        actividad_id = actividad_data.get('id')
        pei_id = actividad_data.get('pei')
        
        # 3. Convertir tipos de datos
        actividad_procesada = self._convertir_datos_actividad(actividad_data)
        
        # 4. Procesar responsable
        if 'responsable' in actividad_procesada:
            actividad_procesada['responsable'] = self._obtener_responsable(
                actividad_procesada['responsable']
            )
        
        # 5. Procesar tipo - ¡CORREGIDO!
        if 'tipo' in actividad_procesada:
            actividad_procesada['tipo'] = self._obtener_tipo_actividad(
                actividad_procesada['tipo']
            )
        
        # 6. Verificar que el PEI existe
        try:
            pei = Pei.objects.get(id=pei_id)
        except Pei.DoesNotExist:
            raise ValueError(f"No existe PEI con ID {pei_id}")
        
        # 7. Crear o actualizar actividad
        if actividad_id:
            # Buscar actividad existente
            try:
                actividad = ActividadPei.objects.get(id=actividad_id, pei_id=pei_id)
                created = False
                
                # Actualizar campos
                for key, value in actividad_procesada.items():
                    if key not in ['id', 'pei']:  # No actualizar ID ni PEI
                        setattr(actividad, key, value)
                
                actividad.save()
                
            except ActividadPei.DoesNotExist:
                # Crear nueva actividad
                actividad = ActividadPei.objects.create(**actividad_procesada)
                created = True
        else:
            # Crear nueva actividad
            actividad = ActividadPei.objects.create(**actividad_procesada)
            created = True
        
        # 8. Actualizar relaciones many-to-many si existen
        self._actualizar_relaciones_actividad(actividad, actividad_data)
        
        return actividad, created
    
    def _convertir_datos_actividad(self, actividad_data):
        """
        Convierte los datos de la actividad a tipos correctos.
        """
        resultado = {}
        
        for key, value in actividad_data.items():
            # Saltar relaciones many-to-many (se manejan después)
            if key in ['objetivos_pei', 'factores_criticos', 
                      'indicadores_cuantitativos', 'indicadores_cualitativos',
                      'procedencia_fondos']:
                continue
            
            # Convertir valores vacíos a None
            if value == '' or value == 'null' or value is None:
                resultado[key] = None
                continue
            
            # Manejar campos específicos
            if key == 'presupuesto':
                try:
                    resultado[key] = float(value) if value is not None else 0.0
                except (ValueError, TypeError):
                    resultado[key] = 0.0
            
            elif key in ['presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo']:
                try:
                    resultado[key] = float(value) if value is not None else 0.0
                except (ValueError, TypeError):
                    resultado[key] = 0.0
            
            elif key == 'estaInactiva':
                if isinstance(value, str):
                    resultado[key] = value.lower() in ['true', '1', 'yes', 'si']
                else:
                    resultado[key] = bool(value)
            
            elif key in ['fecha_programada', 'fecha_inicio', 'fecha_cierre']:
                # Las fechas se manejan automáticamente por Django
                resultado[key] = value
            
            else:
                resultado[key] = value
        
        # Manejar procedencia_fondos por separado (es un JSONField)
        if 'procedencia_fondos' in actividad_data:
            resultado['procedencia_fondos'] = actividad_data['procedencia_fondos']
        
        return resultado
    
    def _obtener_responsable(self, responsable_data):
        """
        Obtiene el objeto Usuario desde username o ID.
        """
        if not responsable_data:
            return None
        
        if isinstance(responsable_data, Usuario):
            return responsable_data
        
        if isinstance(responsable_data, str):
            try:
                return Usuario.objects.get(username=responsable_data)
            except Usuario.DoesNotExist:
                # Intentar por ID si es numérico
                if responsable_data.isdigit():
                    try:
                        return Usuario.objects.get(id=int(responsable_data))
                    except Usuario.DoesNotExist:
                        return None
                return None
        
        if isinstance(responsable_data, int):
            try:
                return Usuario.objects.get(id=responsable_data)
            except Usuario.DoesNotExist:
                return None
        
        return None
    
    def _obtener_tipo_actividad(self, tipo_data):
        """
        Obtiene el objeto TipoActividad desde string o ID.
        CORREGIDO: Ahora busca por 'sigla' o 'tipo_actividad' en lugar de 'codigo'
        """
        if not tipo_data:
            return None
        
        if isinstance(tipo_data, TipoActividad):
            return tipo_data
        
        if isinstance(tipo_data, int):
            try:
                return TipoActividad.objects.get(id=tipo_data)
            except TipoActividad.DoesNotExist:
                return None
        
        if isinstance(tipo_data, str):
            # Caso: 'NODEF' o vacío
            if tipo_data == 'NODEF' or tipo_data == '' or tipo_data.lower() == 'null':
                return None
            
            # Caso 1: Formato "CSNS - Campaña de Sensibilización"
            if ' - ' in tipo_data:
                # Extraer la sigla (primera parte antes de " - ")
                sigla = tipo_data.split(' - ')[0].strip()
                
                # Buscar por sigla
                try:
                    return TipoActividad.objects.get(sigla=sigla)
                except TipoActividad.DoesNotExist:
                    # Buscar por tipo_actividad que contenga la sigla o descripción
                    nombre_busqueda = tipo_data.split(' - ')[1].strip() if len(tipo_data.split(' - ')) > 1 else tipo_data
                    return TipoActividad.objects.filter(
                        Q(tipo_actividad__icontains=nombre_busqueda) |
                        Q(sigla__icontains=sigla)
                    ).first()
            
            # Caso 2: Solo sigla (ej: "CSNS")
            try:
                return TipoActividad.objects.get(sigla=tipo_data)
            except TipoActividad.DoesNotExist:
                pass
            
            # Caso 3: Buscar por tipo_actividad que contenga el string
            tipo = TipoActividad.objects.filter(
                tipo_actividad__icontains=tipo_data
            ).first()
            
            if tipo:
                return tipo
            
            # Caso 4: Buscar por sigla que contenga el string
            tipo = TipoActividad.objects.filter(
                sigla__icontains=tipo_data
            ).first()
            
            return tipo
        
        return None
    
    def _actualizar_relaciones_actividad(self, actividad, actividad_data):
        """
        Actualiza las relaciones many-to-many de la actividad.
        """
        from spme_estructuracion_pei.models import (
            ObjetivoPei, FactoresCriticos, 
            IndicadorPeiCuantitativo, IndicadorPeiCualitativo
        )
        
        # Objetivos PEI
        if 'objetivos_pei' in actividad_data and actividad_data['objetivos_pei']:
            try:
                objetivos_ids = [obj['id'] for obj in actividad_data['objetivos_pei'] if 'id' in obj]
                if objetivos_ids:
                    objetivos = ObjetivoPei.objects.filter(id__in=objetivos_ids)
                    actividad.objetivos_pei.set(objetivos)
            except Exception as e:
                print(f"⚠️ Error actualizando objetivos_pei: {e}")
        
        # Factores críticos
        if 'factores_criticos' in actividad_data and actividad_data['factores_criticos']:
            try:
                factores_ids = [fc['id'] for fc in actividad_data['factores_criticos'] if 'id' in fc]
                if factores_ids:
                    factores = FactoresCriticos.objects.filter(id__in=factores_ids)
                    actividad.factores_criticos.set(factores)
            except Exception as e:
                print(f"⚠️ Error actualizando factores_criticos: {e}")
        
        # Indicadores cuantitativos
        if 'indicadores_cuantitativos' in actividad_data and actividad_data['indicadores_cuantitativos']:
            try:
                indicadores_ids = [ind['id'] for ind in actividad_data['indicadores_cuantitativos'] if 'id' in ind]
                if indicadores_ids:
                    indicadores = IndicadorPeiCuantitativo.objects.filter(id__in=indicadores_ids)
                    actividad.indicadores_cuantitativos.set(indicadores)
            except Exception as e:
                print(f"⚠️ Error actualizando indicadores_cuantitativos: {e}")
        
        # Indicadores cualitativos
        if 'indicadores_cualitativos' in actividad_data and actividad_data['indicadores_cualitativos']:
            try:
                indicadores_ids = [ind['id'] for ind in actividad_data['indicadores_cualitativos'] if 'id' in ind]
                if indicadores_ids:
                    indicadores = IndicadorPeiCualitativo.objects.filter(id__in=indicadores_ids)
                    actividad.indicadores_cualitativos.set(indicadores)
            except Exception as e:
                print(f"⚠️ Error actualizando indicadores_cualitativos: {e}")
    
    def _crear_planificacion_simple(self, seguimiento_data, usuario, actividades_procesadas):
        """
        Crea un registro de PlanificacionPei de forma simplificada.
        """
        # 1. Validar datos mínimos
        pei_id = seguimiento_data.get('pei')
        if not pei_id:
            raise ValueError("El seguimiento debe tener un PEI asociado")
        
        # 2. Verificar que el PEI existe
        try:
            Pei.objects.get(id=pei_id)
        except Pei.DoesNotExist:
            raise ValueError(f"No existe PEI con ID {pei_id}")
        
        # 3. Obtener usuarios
        creado_por_id = seguimiento_data.get('creado_por')
        actualizado_por_id = seguimiento_data.get('actualizado_por')
        
        creado_por = self._obtener_usuario_por_id(creado_por_id, usuario)
        actualizado_por = self._obtener_usuario_por_id(actualizado_por_id, usuario)
        
        # 4. Determinar versión
        ultima_version = PlanificacionPei.objects.filter(
            pei_id=pei_id
        ).aggregate(Max('version'))['version__max']
        
        version = (ultima_version or 0) + 1
        
        # 5. Calcular estadísticas básicas
        total_actividades = len(actividades_procesadas)
        
        total_presupuesto = 0
        for act in actividades_procesadas:
            try:
                total_presupuesto += float(act.presupuesto or 0)
            except (ValueError, TypeError):
                pass
        
        actividades_planificadas = 0
        for act in actividades_procesadas:
            if act.fecha_inicio and act.fecha_cierre:
                actividades_planificadas += 1
        
        # 6. Crear planificación
        planificacion = PlanificacionPei.objects.create(
            pei_id=pei_id,
            datos_tabla_actual=seguimiento_data.get('datos_tabla_actual', []),
            datos_tabla_actualizado=seguimiento_data.get('datos_tabla_actualizado', []),
            cambios_efectuados=seguimiento_data.get('cambios_efectuados', {}),
            configuracion=seguimiento_data.get('configuracion', {}),
            version=version,
            creado_por=creado_por,
            actualizado_por=actualizado_por,
            total_actividades=total_actividades,
            total_presupuesto=total_presupuesto,
            actividades_planificadas=actividades_planificadas,
            total_subactividades=0
        )
        
        return planificacion
    
    def _obtener_usuario_por_id(self, usuario_id, usuario_por_defecto):
        """
        Obtiene usuario por ID o retorna el por defecto.
        """
        if usuario_id:
            try:
                return Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                print(f"⚠️ Usuario con ID {usuario_id} no encontrado, usando por defecto")
        
        return usuario_por_defecto
    
    def _build_success_response_simple(self, planificacion, actividades_resultados):
        """
        Construye respuesta exitosa simplificada.
        """
        response_data = {
            'success': True,
            'message': 'Planificación procesada exitosamente',
            'planificacion_id': planificacion.id,
            'version': planificacion.version,
            'pei_id': planificacion.pei_id,
            'estadisticas': {
                'total_actividades': planificacion.total_actividades,
                'total_presupuesto': float(planificacion.total_presupuesto),
                'actividades_planificadas': planificacion.actividades_planificadas
            },
            'actividades': {
                'total': actividades_resultados['total'],
                'creadas': actividades_resultados['creadas'],
                'actualizadas': actividades_resultados['actualizadas'],
                'fallidas': len(actividades_resultados['fallidas'])
            }
        }
        
        # Incluir detalles de fallas solo si existen
        if actividades_resultados['fallidas']:
            response_data['actividades']['detalles_fallidos'] = actividades_resultados['fallidas']
            # También incluir un resumen para debugging
            response_data['debug'] = {
                'errores_tipo': 'Error al buscar TipoActividad por código',
                'sugerencia': 'Verificar que los tipos en el frontend coincidan con los registros en TipoActividad'
            }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def _handle_error(self, error):
        """
        Maneja errores de forma simplificada.
        """
        # Imprimir error completo para debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error completo:\n{error_details}")
        
        response_data = {
            'success': False,
            'error': str(error),
            'timestamp': timezone.now().isoformat()
        }
        
        # Determinar código de estado apropiado
        error_str = str(error)
        if "No existe PEI" in error_str:
            status_code = status.HTTP_404_NOT_FOUND
            response_data['tipo_error'] = 'PEI_NO_ENCONTRADO'
        elif "Debe proporcionar" in error_str or "inválid" in error_str.lower():
            status_code = status.HTTP_400_BAD_REQUEST
            response_data['tipo_error'] = 'DATOS_INVALIDOS'
        elif "Cannot resolve keyword 'codigo'" in error_str:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data['tipo_error'] = 'TIPO_ACTIVIDAD_NO_ENCONTRADO'
            response_data['sugerencia'] = 'El campo "codigo" no existe en TipoActividad. Verificar nombres de campos.'
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data['tipo_error'] = 'ERROR_INTERNO'
        
        return Response(response_data, status=status_code)


# Versión alternativa más simple y directa
class ProcesarPlanificacionDirectaView(APIView):
    """
    Versión ultra-simplificada que maneja directamente los tipos de actividades.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Procesa las actividades de manera directa, sin serializer complejo.
        """
        data = request.data
        
        # Validaciones básicas
        if not data.get('actividades'):
            return Response({
                'success': False,
                'error': 'Debe proporcionar actividades'
            }, status=400)
        
        if not data.get('seguimiento'):
            return Response({
                'success': False,
                'error': 'Debe proporcionar seguimiento'
            }, status=400)
        
        try:
            with transaction.atomic():
                # 1. Mapeo de tipos de actividad
                tipo_actividad_map = self._crear_mapa_tipos_actividad()
                
                # 2. Procesar actividades
                actividades_procesadas = []
                fallidas = []
                
                for actividad_data in data['actividades']:
                    try:
                        actividad = self._procesar_actividad_directa(
                            actividad_data, 
                            tipo_actividad_map
                        )
                        actividades_procesadas.append(actividad)
                    except Exception as e:
                        fallidas.append({
                            'codigo': actividad_data.get('codigo'),
                            'error': str(e)
                        })
                
                # 3. Crear planificación
                planificacion = self._crear_planificacion_directa(
                    data['seguimiento'],
                    request.user,
                    actividades_procesadas
                )
                
                return Response({
                    'success': True,
                    'planificacion_id': planificacion.id,
                    'version': planificacion.version,
                    'actividades_procesadas': len(actividades_procesadas),
                    'actividades_fallidas': len(fallidas),
                    'fallidas': fallidas if fallidas else None
                }, status=201)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    def _crear_mapa_tipos_actividad(self):
        """
        Crea un mapa de tipos de actividad para búsqueda rápida.
        """
        tipos = TipoActividad.objects.all()
        mapa = {}
        
        for tipo in tipos:
            # Mapear por sigla
            if tipo.sigla:
                mapa[tipo.sigla] = tipo
            
            # Mapear por tipo_actividad
            if tipo.tipo_actividad:
                # Tomar solo las primeras palabras si es muy largo
                clave = tipo.tipo_actividad.split()[0] if ' ' in tipo.tipo_actividad else tipo.tipo_actividad
                mapa[clave] = tipo
        
        # Agregar mapeos comunes
        mapeos_comunes = {
            'CSNS': self._buscar_tipo_por_sigla('CSNS'),
            'AOP': self._buscar_tipo_por_sigla('AOP'),
            'NODEF': None,
        }
        
        mapa.update(mapeos_comunes)
        return mapa
    
    def _buscar_tipo_por_sigla(self, sigla):
        """Busca tipo por sigla"""
        try:
            return TipoActividad.objects.get(sigla=sigla)
        except TipoActividad.DoesNotExist:
            return None
    
    def _procesar_actividad_directa(self, actividad_data, tipo_map):
        """Procesa una actividad directamente"""
        # Extraer datos básicos
        actividad_id = actividad_data.get('id')
        pei_id = actividad_data.get('pei')
        
        if not pei_id:
            raise ValueError("Actividad sin PEI")
        
        # Determinar tipo de actividad
        tipo_str = actividad_data.get('tipo', '')
        tipo_objeto = None
        
        if tipo_str:
            # Formato "CSNS - Campaña de Sensibilización"
            if ' - ' in tipo_str:
                sigla = tipo_str.split(' - ')[0].strip()
                tipo_objeto = tipo_map.get(sigla)
            else:
                # Buscar directo
                tipo_objeto = tipo_map.get(tipo_str)
        
        # Crear/actualizar actividad
        if actividad_id:
            try:
                actividad = ActividadPei.objects.get(id=actividad_id, pei_id=pei_id)
                
                # Actualizar campos
                for field in ['codigo', 'nombreCorto', 'descripcion', 'fecha_inicio', 
                            'fecha_cierre', 'presupuesto', 'estado']:
                    if field in actividad_data:
                        setattr(actividad, field, actividad_data[field])
                
                # Actualizar tipo
                if tipo_objeto is not None:
                    actividad.tipo = tipo_objeto
                elif tipo_str == 'NODEF' or tipo_str == '':
                    actividad.tipo = None
                
                actividad.save()
                
            except ActividadPei.DoesNotExist:
                # Crear nueva
                actividad = ActividadPei.objects.create(
                    pei_id=pei_id,
                    codigo=actividad_data.get('codigo'),
                    nombreCorto=actividad_data.get('nombreCorto'),
                    tipo=tipo_objeto,
                    # ... otros campos
                )
        else:
            # Crear nueva
            actividad = ActividadPei.objects.create(
                pei_id=pei_id,
                codigo=actividad_data.get('codigo'),
                nombreCorto=actividad_data.get('nombreCorto'),
                tipo=tipo_objeto,
                # ... otros campos según necesidad
            )
        
        return actividad
    
    def _crear_planificacion_directa(self, seguimiento_data, usuario, actividades):
        """Crea planificación directamente"""
        pei_id = seguimiento_data.get('pei')
        
        # Determinar versión
        ultima_version = PlanificacionPei.objects.filter(
            pei_id=pei_id
        ).aggregate(Max('version'))['version__max']
        
        version = (ultima_version or 0) + 1
        
        return PlanificacionPei.objects.create(
            pei_id=pei_id,
            datos_tabla_actual=seguimiento_data.get('datos_tabla_actual', []),
            datos_tabla_actualizado=seguimiento_data.get('datos_tabla_actualizado', []),
            cambios_efectuados=seguimiento_data.get('cambios_efectuados', {}),
            configuracion=seguimiento_data.get('configuracion', {}),
            version=version,
            creado_por=usuario,
            actualizado_por=usuario,
            total_actividades=len(actividades),
            total_presupuesto=sum(float(a.presupuesto or 0) for a in actividades),
            actividades_planificadas=sum(1 for a in actividades if a.fecha_inicio and a.fecha_cierre)
        )