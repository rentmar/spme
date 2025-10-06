# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.apps import apps
from decimal import Decimal
import logging
from spme_monitoreo.models import InfActividad
from ..serializers.crear_informe_de_actividad_serializer import InformeActividadCreateSerializer, InfActividadSerializer

logger = logging.getLogger(__name__)

class InfActividadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Informes de Actividad con procesamiento completo y transacciones atómicas
    """
    queryset = InfActividad.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return InformeActividadCreateSerializer
        return InfActividadSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Endpoint principal para crear informes con procesamiento completo
        Transacción atómica garantizada por el decorador @transaction.atomic
        """
        logger.info("📨 SOLICITUD DE CREACIÓN DE INFORME RECIBIDA")
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"❌ ERROR DE VALIDACIÓN: {serializer.errors}")
            return Response(
                {
                    'success': False,
                    'message': 'Error de validación en los datos',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info("🔄 INICIANDO PROCESAMIENTO EN TRANSACCIÓN ATÓMICA...")
            
            # Obtener modelos
            InfActividad = apps.get_model('spme_monitoreo', 'InfActividad')
            Actividad = apps.get_model('spme_actividades', 'Actividad')
            
            datos_validados = serializer.validated_data
            actividad_id = datos_validados.get('actividad_id')
            
            # Validar que la actividad existe
            try:
                actividad = Actividad.objects.get(id=actividad_id)
                logger.info(f"✅ Actividad encontrada: {actividad.codigo}")
            except Actividad.DoesNotExist:
                raise ValueError(f"❌ Actividad con ID {actividad_id} no encontrada")
            
            # PASO 1: Generar número de informe único
            logger.info("📝 PASO 1: Generando número de informe único...")
            numero_informe = self._generar_numero_informe()
            logger.info(f"✅ Número de informe: {numero_informe}")
            
            # PASO 2: Crear el informe en InfActividad
            logger.info("📋 PASO 2: Creando registro en InfActividad...")
            informe = self._crear_informe_actividad(datos_validados, numero_informe, InfActividad)
            logger.info(f"✅ Informe creado - ID: {informe.id}")
            
            # PASO 3: Actualizar totalReportado en Actividad
            logger.info("💰 PASO 3: Actualizando totalReportado en Actividad...")
            self._actualizar_total_reportado(datos_validados, actividad)
            logger.info("✅ Total reportado actualizado")
            
            # PASO 4: Procesar bitácoras de indicadores
            logger.info("📊 PASO 4: Procesando bitácoras de indicadores...")
            bitacoras_creadas = self._procesar_bitacoras_indicadores(datos_validados, informe)
            logger.info(f"✅ Bitácoras procesadas: {len(bitacoras_creadas)} registros")
            
            logger.info("🎉 TRANSACCIÓN COMPLETADA EXITOSAMENTE")
            
            # Serializar respuesta
            output_serializer = InfActividadSerializer(informe)
            
            return Response(
                {
                    'success': True,
                    'message': 'Informe procesado exitosamente',
                    'data': output_serializer.data,
                    'metadata': {
                        'numero_informe': numero_informe,
                        'bitacoras_creadas': len(bitacoras_creadas)
                    }
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"💥 ERROR EN TRANSACCIÓN: {str(e)}")
            logger.error("🔄 TRANSACCIÓN REVERTIDA - NINGÚN DATO GUARDADO")
            # La transacción se revertirá automáticamente aquí
            
            return Response(
                {
                    'success': False,
                    'message': f'Error procesando el informe: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generar_numero_informe(self):
        """Genera número de informe único: INF-YYYYMMDD-XXXX"""
        InfActividad = apps.get_model('spme_monitoreo', 'InfActividad')
        timestamp = timezone.now()
        fecha_str = timestamp.strftime('%Y%m%d')
        
        with transaction.atomic():
            ultimo_informe = InfActividad.objects.filter(
                numeroInforme__startswith=f"INF-{fecha_str}"
            ).order_by('-numeroInforme').first()
            
            if ultimo_informe:
                try:
                    ultima_secuencia = int(ultimo_informe.numeroInforme.split('-')[-1])
                    secuencia = ultima_secuencia + 1
                except (ValueError, IndexError):
                    secuencia = 1
            else:
                secuencia = 1
            
            return f"INF-{fecha_str}-{secuencia:04d}"
    
    def _crear_informe_actividad(self, datos_validados, numero_informe, InfActividad):
        """Crea el registro en InfActividad"""
        logger.debug("Mapeando datos del formulario al modelo InfActividad...")
        
        # Mapeo de campos
        campo_mapping = {
            'fecha_ejecucion': 'fecha_ejecucion',
            'objetivo_de_actividad': 'objetivo_actividad',
            'informe_de_objetivo_de_actividad': 'informe_objetivo_actividad',
            'tipo_de_actividad': 'tipo_actividad',
            'reporte_tipo': 'reporte_tipo',
            'informacion_cuantitativa': 'informacion_cuantitativa',
            'descripcion_herramientas': 'herramientas_evaluacion',
            'medios_verificacion': 'medios_verificacion',
            'comentarios_recomendaciones': 'comentarios_recomendaciones',
            'observaciones_presupuesto': 'observaciones_presupuesto',
        }
        
        informe_data = {
            'numeroInforme': numero_informe,
            'actividad_id': datos_validados.get('actividad_id')
        }
        
        # Mapear campos directos
        for campo_form, campo_model in campo_mapping.items():
            if campo_form in datos_validados:
                informe_data[campo_model] = datos_validados[campo_form]
                logger.debug(f"Campo mapeado: {campo_form} -> {campo_model}")
        
        # Campos JSON
        json_fields = {
            'contribucion_actividad': 'contribucion_proyecto',
            'avance_en_indicador': 'avance_indicadores',
            'procedencia_fondos': 'procedencia_fondos'
        }
        
        for campo_form, campo_model in json_fields.items():
            if campo_form in datos_validados:
                informe_data[campo_model] = datos_validados[campo_form]
                logger.debug(f"Campo JSON mapeado: {campo_form} -> {campo_model}")
        
        # Campos de archivos
        archivo_fields = ['archivos_cuantitativos', 'herramientas_archivos', 'medios_archivos']
        for campo_archivo in archivo_fields:
            if campo_archivo in datos_validados:
                informe_data[campo_archivo] = datos_validados[campo_archivo]
                logger.debug(f"Archivos mapeados: {campo_archivo}")
        
        # Campos de presupuesto
        if 'total_planificado' in datos_validados:
            informe_data['presupuesto_planificado'] = Decimal(str(datos_validados['total_planificado']))
            logger.debug(f"Presupuesto planificado: {informe_data['presupuesto_planificado']}")
        
        if 'total_ejecutado' in datos_validados:
            informe_data['presupuesto_ejecutado'] = Decimal(str(datos_validados['total_ejecutado']))
            logger.debug(f"Presupuesto ejecutado: {informe_data['presupuesto_ejecutado']}")
        
        logger.info(f"Creando informe con {len(informe_data)} campos...")
        
        return InfActividad.objects.create(**informe_data)
    
    def _actualizar_total_reportado(self, datos_validados, actividad):
        """Actualiza totalReportado en Actividad"""
        total_ejecutado = datos_validados.get('total_ejecutado')
        
        if total_ejecutado is None:
            logger.warning("⚠️ total_ejecutado no proporcionado, saltando actualización")
            return
        
        total_ejecutado_decimal = Decimal(str(total_ejecutado))
        logger.info(f"Actualizando totalReportado de {actividad.totalReportado} a {total_ejecutado_decimal}")
        
        actividad.totalReportado = total_ejecutado_decimal
        actividad.save()
        
        logger.info(f"✅ Actividad {actividad.id} - totalReportado actualizado exitosamente")
    
    def _procesar_bitacoras_indicadores(self, datos_validados, informe):
        """Procesa las bitácoras de indicadores"""
        avance_indicadores = datos_validados.get('avance_en_indicador')
        
        if not avance_indicadores:
            logger.info("ℹ️ No hay datos de avance de indicadores para procesar")
            return []
        
        if not isinstance(avance_indicadores, dict) or 'datos' not in avance_indicadores:
            logger.warning("⚠️ Estructura de avance_indicadores inválida")
            return []
        
        datos = avance_indicadores.get('datos', [])
        logger.info(f"Procesando {len(datos)} indicadores...")
        
        bitacoras_creadas = []
        
        # Obtener modelos de bitácoras
        modelos_bitacora = {
            'indicadorog': apps.get_model('spme_proyectos_reportes', 'BitacoraIndicadorOG'),
            'indicadoroe': apps.get_model('spme_proyectos_reportes', 'BitacoraIndicadorOE'),
            'indicadorrog': apps.get_model('spme_proyectos_reportes', 'BitacoraIndicadorROG'),
            'indicadorroe': apps.get_model('spme_proyectos_reportes', 'BitacoraIndicadorROE'),
        }
        
        # Obtener modelos de indicadores
        modelos_indicador = {
            'indicadorog': apps.get_model('spme_estructuracion_proyecto', 'IndicadorObjetivoGeneral'),
            'indicadoroe': apps.get_model('spme_estructuracion_proyecto', 'IndicadorObjetivoEspecifico'),
            'indicadorrog': apps.get_model('spme_estructuracion_proyecto', 'IndicadorResultadoObjGral'),
            'indicadorroe': apps.get_model('spme_estructuracion_proyecto', 'IndicadorResultadoObjEspecifico'),
        }
        
        for i, dato_indicador in enumerate(datos):
            try:
                logger.info(f"Procesando indicador {i+1}/{len(datos)}...")
                bitacora = self._crear_bitacora_individual(
                    dato_indicador, informe, modelos_bitacora, modelos_indicador
                )
                if bitacora:
                    bitacoras_creadas.append(bitacora)
                    logger.info(f"✅ Bitácora creada para indicador {dato_indicador.get('id')}")
                else:
                    logger.warning(f"⚠️ No se pudo crear bitácora para indicador {dato_indicador.get('id')}")
                    
            except Exception as e:
                logger.error(f"💥 Error procesando indicador {dato_indicador.get('id')}: {str(e)}")
                raise  # Relanzar para revertir la transacción
        
        return bitacoras_creadas
    
    def _crear_bitacora_individual(self, dato_indicador, informe, modelos_bitacora, modelos_indicador):
        """Crea una bitácora individual"""
        tipo_indicador = dato_indicador.get('type')
        nodoproyecto = dato_indicador.get('nodoproyecto', {})
        tipo_dato = dato_indicador.get('tipo_dato')
        datos_registrados = dato_indicador.get('datosRegistrados', {})
        
        # CORRECCIÓN: Usar nodoproyecto.id en lugar del id del primer nivel
        id_indicador_str = nodoproyecto.get('id')  # ← ESTA ES LA CORRECCIÓN
        
        # Validaciones básicas
        if not all([tipo_indicador, id_indicador_str, tipo_dato, datos_registrados]):
            logger.warning(f"⚠️ Datos incompletos para bitácora: {dato_indicador}")
            return None
        
        if tipo_indicador not in modelos_bitacora:
            logger.warning(f"⚠️ Tipo de indicador no soportado: {tipo_indicador}")
            return None
        
        # Convertir ID a entero
        try:
            id_indicador = int(id_indicador_str)
        except (ValueError, TypeError):
            logger.warning(f"⚠️ ID de indicador inválido: {id_indicador_str}")
            return None
        
        # Preparar datos
        bitacora_data = {
            'tipo_indicador': tipo_indicador,
            'tipo_dato': tipo_dato,
            'id_indicador': id_indicador,
            'fecha_registro': datos_registrados.get('fecha_registro'),
            'observaciones': datos_registrados.get('observaciones', ''),
            'archivos_adjuntos': datos_registrados.get('archivos', []),
            'timestamp_registro': datos_registrados.get('timestamp'),
            'informe_actividad': informe,
            'snapshot_indicador': nodoproyecto,
        }
        
        # Asignar valor según tipo de dato
        valor = datos_registrados.get('valor')
        if tipo_dato == 'A-Z':
            bitacora_data['valor_literal'] = str(valor) if valor else ''
        elif tipo_dato == '1-9':
            try:
                bitacora_data['valor_numerico'] = Decimal(str(valor)) if valor else None
            except (ValueError, TypeError):
                bitacora_data['valor_numerico'] = None
        elif tipo_dato == '%':
            try:
                bitacora_data['valor_porcentual'] = Decimal(str(valor)) if valor else None
            except (ValueError, TypeError):
                bitacora_data['valor_porcentual'] = None
        
        # Crear bitácora específica
        modelo_bitacora = modelos_bitacora[tipo_indicador]
        modelo_indicador = modelos_indicador[tipo_indicador]
        
        # Verificar que el indicador existe
        try:
            indicador = modelo_indicador.objects.get(id=id_indicador)
            logger.info(f"✅ Indicador encontrado: {tipo_indicador} ID {id_indicador} - {indicador.codigo}")
        except modelo_indicador.DoesNotExist:
            logger.warning(f"⚠️ Indicador no encontrado: {tipo_indicador} ID {id_indicador}")
            return None
        
        # Crear la bitácora con el FK específico
        try:
            if tipo_indicador == 'indicadorog':
                bitacora = modelo_bitacora.objects.create(indicador_og=indicador, **bitacora_data)
            elif tipo_indicador == 'indicadoroe':
                bitacora = modelo_bitacora.objects.create(indicador_oe=indicador, **bitacora_data)
            elif tipo_indicador == 'indicadorrog':
                bitacora = modelo_bitacora.objects.create(indicador_rog=indicador, **bitacora_data)
            elif tipo_indicador == 'indicadorroe':
                bitacora = modelo_bitacora.objects.create(indicador_roe=indicador, **bitacora_data)
            else:
                return None
            
            logger.info(f"✅ Bitácora creada exitosamente: {bitacora.id} para indicador {id_indicador}")
            return bitacora
            
        except Exception as e:
            logger.error(f"💥 Error creando bitácora para indicador {id_indicador}: {str(e)}")
            return None