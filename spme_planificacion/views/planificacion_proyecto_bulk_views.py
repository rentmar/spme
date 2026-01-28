# views.py 
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils.dateparse import parse_date
from spme_actividades.models import Actividad, TipoActividad
# from .models import Actividad
# from .serializers import ActividadSerializer
from ..serializers.planificacion_proyecto_bulk_serializer import ActividadSerializer
from spme_autenticacion.models import Usuario
from spme_estructuracion_proyecto.models import Proyecto
from spme_estructuracion_pei.models import ObjetivoPei, IndicadorPeiBase

class ActividadProyectoViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    
    @action(detail=False, methods=['post'], url_path='procesar-actividades')
    def procesar_actividades(self, request):
        """
        Endpoint corregido - usa el campo correcto para TipoActividad
        """
        try:
            # Obtener datos
            data = request.data
            
            # Determinar formato
            if isinstance(data, list):
                actividades_data = data
            elif isinstance(data, dict) and 'actividades' in data:
                actividades_data = data['actividades']
            elif isinstance(data, dict):
                actividades_data = [data]
            else:
                return Response(
                    {'error': 'Formato no válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not actividades_data:
                return Response(
                    {'error': 'No se encontraron actividades'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            resultados = []
            errores = []
            
            with transaction.atomic():
                for idx, act_data in enumerate(actividades_data):
                    try:
                        # Procesar actividad
                        actividad = self._procesar_actividad_corregida(act_data)
                        
                        resultados.append({
                            'id': actividad.id,
                            'codigo': actividad.codigo,
                            'nombre': actividad.nombreCorto,
                            'tipo': str(actividad.tipo) if actividad.tipo else None,
                            'estado': 'actualizada' if act_data.get('id') else 'creada'
                        })
                        
                    except Exception as e:
                        errores.append({
                            'indice': idx,
                            'actividad': act_data.get('codigo', f'Item-{idx}'),
                            'error': str(e),
                            'datos_relevantes': {
                                'tipo': act_data.get('tipo'),
                                'proyecto': act_data.get('proyecto'),
                                'responsable': act_data.get('responsable')
                            }
                        })
            
            return Response({
                'total': len(actividades_data),
                'exitosas': len(resultados),
                'fallidas': len(errores),
                'resultados': resultados,
                'errores': errores if errores else None
            }, status=status.HTTP_207_MULTI_STATUS if errores else status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            return Response({
                'error': 'Error general en el servidor',
                'detalle': str(e),
                'traceback': traceback.format_exc() if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _procesar_actividad_corregida(self, data):
        """
        Procesar actividad usando el campo correcto para TipoActividad
        """
        # Extraer ID para determinar si es update o create
        actividad_id = data.get('id')
        
        # Preparar datos para el modelo
        model_data = {}
        
        # Campos directos del modelo
        campos_directos = [
            'codigo', 'nombreCorto', 'descripcion', 'supuestos', 'riesgos',
            'objetivo_de_actividad', 'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'estado', 'rutaTrazadoIndicadores', 'factoresCriticos', 'estructuraProcedencia'
        ]
        
        for campo in campos_directos:
            if campo in data:
                model_data[campo] = data[campo]
        
        # Campos con conversión especial
        # Fechas
        for fecha_field in ['fecha_programada', 'fecha_inicio', 'fecha_cierre']:
            if fecha_field in data and data[fecha_field]:
                try:
                    model_data[fecha_field] = parse_date(data[fecha_field])
                except:
                    model_data[fecha_field] = None
        
        # Campos numéricos
        for num_field in ['presupuesto', 'presupuestoGlobal', 'totalReportado',
                         'totalEjecutado', 'saldo']:
            if num_field in data and data[num_field] not in [None, '']:
                try:
                    value = str(data[num_field]).replace(',', '')
                    model_data[num_field] = float(value) if '.' in value else int(value)
                except:
                    model_data[num_field] = 0
        
        # Grado de ejecución
        if 'gradoEjecucion' in data:
            model_data['gradoEjecucion'] = data['gradoEjecucion']
        
        # Procedencia fondos (JSON)
        if 'procedencia_fondos' in data:
            model_data['procedencia_fondos'] = data['procedencia_fondos']
        
        # Estado inactiva
        if 'estaInactiva' in data:
            model_data['estaInactiva'] = bool(data['estaInactiva'])
        
        # MANEJAR RELACIONES - CORREGIDO
        # 1. Tipo - CORRECCIÓN PRINCIPAL
        if 'tipo' in data and data['tipo']:
            tipo_input = data['tipo']
            
            # El JSON puede enviar diferentes formatos:
            # - "ACAP"
            # - "CSNS - Campaña de Sensibilización"
            # Necesitamos extraer la sigla
            
            sigla = self._extraer_sigla_tipo(tipo_input)
            
            if sigla:
                try:
                    # Buscar por sigla (no por codigo)
                    tipo_obj = TipoActividad.objects.get(sigla=sigla)
                except TipoActividad.DoesNotExist:
                    # Crear tipo automáticamente
                    # Extraer nombre si está en formato "CSNS - Campaña de Sensibilización"
                    nombre = self._extraer_nombre_tipo(tipo_input, sigla)
                    
                    tipo_obj = TipoActividad.objects.create(
                        sigla=sigla,
                        tipo_actividad=nombre
                    )
                model_data['tipo'] = tipo_obj
        
        # 2. Proyecto
        if 'proyecto' in data and data['proyecto']:
            try:
                proyecto_id = int(data['proyecto'])
                proyecto_obj = Proyecto.objects.get(id=proyecto_id)
                model_data['proyecto'] = proyecto_obj
            except (ValueError, Proyecto.DoesNotExist):
                # Si no existe, puedes crear uno o dejar null
                # Por ahora, dejamos null
                model_data['proyecto'] = None
        
        # 3. Responsable
        if 'responsable' in data and data['responsable']:
            try:
                usuario = Usuario.objects.get(username=data['responsable'])
                model_data['responsable'] = usuario
            except Usuario.DoesNotExist:
                # Asignar null
                model_data['responsable'] = None

        # 4. Objetivo PEI
        if 'objetivo_pei' in data and data['objetivo_pei']:
            try:
                objetivo_id = int(data['objetivo_pei'])
                objetivo_obj = ObjetivoPei.objects.get(id=objetivo_id)
                model_data['objetivo_pei'] = objetivo_obj
            except (ValueError, ObjetivoPei.DoesNotExist):
                model_data['objetivo_pei'] = None        
        
        # 5. Indicador PEI
        if 'indicador_pei' in data and data['indicador_pei']:
            try:
                indicador_id = int(data['indicador_pei'])
                indicador_obj = IndicadorPeiBase.objects.get(id=indicador_id)
                model_data['indicador_pei'] = indicador_obj
            except (ValueError, IndicadorPeiBase.DoesNotExist):
                model_data['indicador_pei'] = None
        
        # 4. Otras relaciones (si existen en tu JSON)
        relaciones = [
            'proceso', 'resultado_og', 'resultado_oe', 'producto_oe'
        ]
        'proceso', 'resultado_og', 'resultado_oe', 'producto_oe'
        
        for rel in relaciones:
            if rel in data and data[rel]:
                try:
                    # Aquí necesitarías importar los modelos correspondientes
                    # y hacer la asignación adecuada
                    # Por ahora, lo omitimos
                    pass
                except:
                    pass
        
        # CREAR O ACTUALIZAR
        if actividad_id:
            try:
                actividad = Actividad.objects.get(id=actividad_id)
                # Actualizar campos
                for key, value in model_data.items():
                    setattr(actividad, key, value)
                actividad.save()
                return actividad
            except Actividad.DoesNotExist:
                # Crear nueva con el ID proporcionado
                model_data['id'] = actividad_id
                return Actividad.objects.create(**model_data)
        else:
            # Crear nueva sin ID específico
            return Actividad.objects.create(**model_data)
    
    def _extraer_sigla_tipo(self, tipo_input):
        """
        Extraer sigla del tipo de actividad
        Ejemplos:
        - "ACAP" -> "ACAP"
        - "CSNS - Campaña de Sensibilización" -> "CSNS"
        - "ACAP - Actividad de Capacitación" -> "ACAP"
        """
        if not tipo_input:
            return None
        
        # Si es solo la sigla
        if len(tipo_input) <= 10 and tipo_input.isalpha():
            return tipo_input
        
        # Si tiene formato "CSNS - Campaña de Sensibilización"
        if ' - ' in tipo_input:
            # Extraer la primera parte antes del " - "
            partes = tipo_input.split(' - ')
            sigla = partes[0].strip()
            # Verificar que sea una sigla válida (todo mayúsculas, 2-10 letras)
            if sigla.isalpha() and 2 <= len(sigla) <= 10:
                return sigla
        
        # Intentar extraer sigla de cualquier forma
        # Buscar la primera palabra en mayúsculas
        palabras = tipo_input.split()
        for palabra in palabras:
            if palabra.isalpha() and palabra.isupper() and 2 <= len(palabra) <= 10:
                return palabra
        
        # Si no encontramos sigla clara, usar las primeras 4 letras
        return tipo_input[:4].upper()
    
    def _extraer_nombre_tipo(self, tipo_input, sigla):
        """
        Extraer nombre completo del tipo de actividad
        """
        if ' - ' in tipo_input:
            # Extraer segunda parte después del " - "
            partes = tipo_input.split(' - ')
            if len(partes) > 1:
                return partes[1].strip()
        
        # Si no tiene formato claro, usar nombres predefinidos
        nombres_predefinidos = {
            'ACAP': 'Actividad de Capacitación',
            'CSNS': 'Campaña de Sensibilización',
            'PRIN': 'Proyecto de Investigación',
            'AOP': 'Actividad Operativa',
            'PDES': 'Proyecto de Desarrollo',
            'AINC': 'Actividad de Incidencia',
            'AART': 'Actividad de Articulación',
            'NODEF': 'No definido',
            'OTRO': 'Otro'
        }
        
        return nombres_predefinidos.get(sigla, tipo_input)
