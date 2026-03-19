# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from spme_monitoreo.models import (
    InformeActividadPrincipal,
    InformeTareaPrincipal
)
from spme_actividades.models import Actividad
from spme_validaciones.models import ValidacionInformeActividad
from spme_autenticacion.models import Usuario
from spme_proyectos_reportes.models import (
    # Modelos PRINCIPALES
    BitacoraPrincipalIndicadorOg,
    BitacoraPrincipalIndicadorOE,
    BitacoraPrincipalIndicadorRog,
    BitacoraPrincipalIndicadorRoe
)
from ..serializers.crear_informe_actividad_principal_serializer import InformeActividadPrincipalSerializer
import json
from datetime import datetime
from decimal import Decimal


class CrearInformeActividadView(APIView):
    """
    Endpoint para crear informes de actividad con transacciones
    INSERTA EN BITÁCORAS PRINCIPALES
    """
    
    # ============================================
    # MÉTODO AUXILIAR - Insertar en bitácora principal
    # ============================================
    def insertar_bitacora_principal(self, modelo, campo_fk, registros, tipo_dato_categoria, informe, tipo_indicador_valor, usuario=None):
        """
        Inserta registros en la bitácora PRINCIPAL correspondiente
        """
        if not registros:
            return 0
        
        print(f"\n   📝 Insertando en {modelo.__name__} ({len(registros)} {tipo_dato_categoria}):")
        print(f"      📌 informe type: {type(informe)}")
        print(f"      📌 informe id: {informe.id if informe else 'None'}")
        print(f"      📌 usuario: {usuario}")
        
        count = 0
        
        for reg in registros:
            if not reg.get('id_indicador'):
                print(f"      ❌ Registro sin id_indicador: {reg}")
                continue
            
            if tipo_dato_categoria == 'literal':
                tipo_dato = 'A-Z'
            elif tipo_dato_categoria == 'porcentual':
                tipo_dato = '%'
            else:
                tipo_dato = '1-9'
            
            kwargs = {
                campo_fk: reg['id_indicador'],
                'tipo_indicador': tipo_indicador_valor,
                'fecha_registro': reg['fecha_registro'],
                'tipo_dato': tipo_dato,
                'observaciones': reg.get('observaciones', ''),
                'timestamp_registro': reg.get('timestamp_registro'),
                'informe_actividad': informe,
                'usuario_registro': usuario,
                'snapshot_indicador': reg.get('registro_completo', reg),
            }
            
            if tipo_dato_categoria == 'literal':
                kwargs['valor_literal'] = reg['valor']
            elif tipo_dato_categoria == 'numerico':
                kwargs['valor_numerico'] = reg['valor']
            else:
                kwargs['valor_porcentual'] = reg['valor']
            
            # 🔍 LOGS DETALLADOS
            print(f"\n      🔍 Intentando crear {modelo.__name__}:")
            print(f"         - {campo_fk}: {kwargs.get(campo_fk)}")
            print(f"         - tipo_indicador: {kwargs.get('tipo_indicador')}")
            print(f"         - fecha_registro: {kwargs.get('fecha_registro')}")
            print(f"         - tipo_dato: {kwargs.get('tipo_dato')}")
            print(f"         - valor: {kwargs.get('valor_literal') or kwargs.get('valor_numerico') or kwargs.get('valor_porcentual')}")
            print(f"         - informe_actividad_id: {kwargs.get('informe_actividad').id if kwargs.get('informe_actividad') else None}")
            print(f"         - usuario_registro_id: {kwargs.get('usuario_registro').id if kwargs.get('usuario_registro') else None}")
            
            try:
                modelo.objects.create(**kwargs)
                count += 1
                print(f"      ✅ CREADO ID {reg['id_indicador']}")
            except Exception as e:
                print(f"      ❌ ERROR: {e}")
                raise
        
        return count
    
    # ============================================
    # MÉTODO AUXILIAR - Insertar validadores
    # ============================================
    def insertar_validadores(self, validadores, informe, usuario_redactor):
        """
        Inserta los validadores para el informe de actividad
        """
        if not validadores:
            print("No hay validadores para insertar")
            return 0
        
        print(f"\n   📝 Insertando {len(validadores)} validador(es):")
        count = 0

        for validador in validadores:
            try:
                # Obtener el ID del validador (puede venir como 'id' o 'id_validador')
                validador_id = validador.get('id')
                if not validador_id:
                    print(f"      ❌ Validador sin ID: {validador}")
                    continue

                #Obtener el objeto usuario del validador
                try:
                    usuario_validador_obj = Usuario.objects.get(id=validador_id)
                except Usuario.DoesNotExist:
                    print(f"      ❌ Usuario validador con ID {validador_id} no encontrado")
                    continue
                # Verificar si ya existe una validación para este usuario en este informe
                existe = ValidacionInformeActividad.objects.filter(
                    informe=informe,
                    usuarioValidador=usuario_validador_obj
                ).exists()

                if existe:
                    print(f"      ⚠️ Ya existe validación para {usuario_validador_obj.username}, saltando...")
                    continue

                # Crear la validación
                validacion = ValidacionInformeActividad.objects.create(
                    informe=informe,
                    usuarioValidador=usuario_validador_obj,
                    usuarioRedactor=usuario_redactor,
                    estado=validador.get('estado', 'PENDIENTE'),
                    comentarios=validador.get('comentarios', 'Nueva Entrada'),
                    versionDocumento=validador.get('versionDocumento', '1'),
                )
                print(f"✅ VALIDADOR CREADO: {validacion.codigoSeguimiento} - {usuario_validador_obj.username}")
                count += 1
            except Exception as e:
                print(f"      ❌ ERROR creando validador: {e}")
                raise  # Re-lanzar la excepción para que la transacción se revierta        
        return count

    # ============================================
    # MÉTODO AUXILIAR - Actualizar actividad
    # ============================================
    def actualizar_actividad(self, informe_data):
        """
        Actualiza los campos de la actividad basados en el informe
        Actualiza: totalReportado, totalEjecutado, saldo
        """
        # Obtener el ID de la actividad
        actividad_id = informe_data.get('actividad')
        if not actividad_id:
            print("⚠️ No se proporcionó ID de actividad para actualizar")
            return None

        try:
            # Buscar la actividad
            actividad = Actividad.objects.get(id=actividad_id)
            print(f"\n📌 Actividad encontrada: {actividad.codigo} (ID: {actividad_id})")
            
            # Obtener valores del informe
            #procedencia_fondos = informe_data.get('procedenciaFondos', {})
            procedencia_fondos = informe_data.get('procedenciaFondos')

            if procedencia_fondos is None or not isinstance(procedencia_fondos, dict):
                print(f"⚠️ procedenciaFondos no es un diccionario válido: {type(procedencia_fondos)}")
                procedencia_fondos = {}

            presupuesto_planificado = informe_data.get('presupuestoPlanificado')
            presupuesto_ejecutado = informe_data.get('presupuestoEjecutado')    
            
            
            print(f"\n📊 Valores extraídos del informe:")
            print(f"   • Presupuesto Ejecutado: {presupuesto_planificado}")
            print(f"   • Presupuesto Planificado: {presupuesto_planificado}")
            
            # Convertir a Decimal
            presupuesto_planificado_decimal = Decimal(str(presupuesto_planificado))
            presupuesto_ejecutado_decimal = Decimal(str(presupuesto_ejecutado))
            saldo = presupuesto_planificado_decimal - presupuesto_ejecutado_decimal 
            
            # Guardar valores anteriores para log
            total_reportado_anterior = actividad.totalReportado
            total_ejecutado_anterior = actividad.totalEjecutado
            saldo_anterior = actividad.saldo
            
            # Actualizar la actividad
            actividad.totalReportado = presupuesto_planificado_decimal
            actividad.totalEjecutado = presupuesto_ejecutado_decimal
            actividad.saldo = saldo
            
            # Actualizar estado si es necesario (opcional)
            if actividad.estado == 'PLAN' or actividad.estado == 'EJEC':
                actividad.estado = 'REP'  # Cambiar a "En Reporte"
            
            actividad.save()
            
            print(f"\n✅ Actividad actualizada:")
            print(f"   • totalReportado: {total_reportado_anterior} → {actividad.totalReportado}")
            print(f"   • totalEjecutado: {total_ejecutado_anterior} → {actividad.totalEjecutado}")
            print(f"   • saldo: {saldo_anterior} → {actividad.saldo}")
            print(f"   • estado: {actividad.estado}")
            
            return actividad
            
        except Actividad.DoesNotExist:
            print(f"❌ Actividad con ID {actividad_id} no encontrada")
            raise Exception(f"Actividad con ID {actividad_id} no encontrada")
        except Exception as e:
            print(f"❌ Error actualizando actividad: {e}")
            raise    



    # ============================================
    # MÉTODO PRINCIPAL POST
    # ============================================
    def post(self, request):
        #Extraer los datos del informe y los validadores del payload
        informe_data = request.data.get('informeData', {})
        validadores_data = request.data.get('validadores', {})

        print("\n" + "="*90)
        print("🔍 RECIBIDA PETICIÓN PARA CREAR INFORME DE ACTIVIDAD")
        print("="*90)
        print(f"📦 Total validadores recibidos: {len(validadores_data)}")
        print(f"INFORME: {informe_data}")
        print(f"VALIDADORES: {validadores_data}")

        #Obtener el usuario
        usuario_id = informe_data.get('usuario')
        usuario_obj = None
        #Si hay id de usuario obtener el objeto
        if usuario_id:
            try:
                usuario_obj = Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                print(f"⚠️ Usuario con ID {usuario_id} no encontrado")    

        print(f"USUARIO: {usuario_obj.__dict__}")

        # 1. Validar serializer
        serializer = InformeActividadPrincipalSerializer(data=informe_data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errores': serializer.errors
                }, status=400)
        
        # 2. Extraer indicadores
        indicadores = informe_data.get('avanceIndicadores')
        if indicadores is None:
            indicadores = {}
        
        print("\n" + "="*90)
        print("🔍 PROCESO DE VERIFICACIÓN DE INDICADORES (BITÁCORAS PRINCIPALES)")
        print("="*90)
        
        # 3. PRIMERA COMPROBACIÓN: ¿Qué tipos de indicadores existen?
        tipos_indicadores = {
            'indicadorog': indicadores.get('indicadorog', []),
            'indicadoroe': indicadores.get('indicadoroe', []),
            'indicadorrog': indicadores.get('indicadorrog', []),
            'indicadorroe': indicadores.get('indicadorroe', [])
        }
        
        print("\n📊 PRIMERA COMPROBACIÓN - TIPOS DE INDICADORES:")
        total_general = 0
        for tipo, lista in tipos_indicadores.items():
            cantidad = len(lista)
            total_general += cantidad
            modelo_destino = {
                'indicadorog': 'BitacoraPrincipalIndicadorOg',
                'indicadoroe': 'BitacoraPrincipalIndicadorOE',
                'indicadorrog': 'BitacoraPrincipalIndicadorRog',
                'indicadorroe': 'BitacoraPrincipalIndicadorRoe'
            }.get(tipo, 'Desconocido')
            
            print(f"   • {tipo}: {cantidad} registro(s) - {'✅ EXISTE' if cantidad > 0 else '❌ VACÍO'} → {modelo_destino}")
        
        print(f"\n   📌 TOTAL GENERAL: {total_general} indicadores")
        
        # 4. SEGUNDA COMPROBACIÓN: Por cada tipo, verificar tipo de dato de CADA registro
        print("\n" + "="*90)
        print("🔍 SEGUNDA COMPROBACIÓN - TIPO DE DATO POR REGISTRO")
        print("="*90)
        
        # Estructura para guardar clasificación por tipo de dato
        clasificacion = {
            'indicadorog': {'literal': [], 'numerico': [], 'porcentual': []},
            'indicadoroe': {'literal': [], 'numerico': [], 'porcentual': []},
            'indicadorrog': {'literal': [], 'numerico': [], 'porcentual': []},
            'indicadorroe': {'literal': [], 'numerico': [], 'porcentual': []}
        }
        
        for tipo, lista in tipos_indicadores.items():
            if not lista:
                print(f"\n📌 {tipo.upper()}: Sin registros")
                continue
                
            print(f"\n📌 {tipo.upper()} ({len(lista)} registros):")
            
            for i, item in enumerate(lista):
                tipo_dato = item.get('tipo_dato')
                id_indicador = item.get('id_indicador')
                
                # Clasificar según tipo_dato
                if tipo_dato == 'A-Z':
                    categoria = 'literal'
                    valor = item.get('valor_literal')
                elif tipo_dato == '%':
                    categoria = 'porcentual'
                    valor = item.get('valor_porcentual')
                else:  # '1-9'
                    categoria = 'numerico'
                    valor = item.get('valor_numerico')
                
                # Guardar en clasificación
                clasificacion[tipo][categoria].append({
                    'id_indicador': id_indicador,
                    'fecha_registro': item.get('fecha_registro'),
                    'valor': valor,
                    'observaciones': item.get('observaciones'),
                    'timestamp_registro': item.get('timestamp_registro'),
                    'registro_completo': item
                })
                
                # Mostrar clasificación
                print(f"   {i+1}. ID {id_indicador} → Tipo: {tipo_dato} ({categoria}) = {valor}")
        
        # 5. RESUMEN DE CLASIFICACIÓN
        print("\n" + "="*90)
        print("📊 RESUMEN DE CLASIFICACIÓN POR TIPO DE DATO")
        print("="*90)
        
        total_literal = 0
        total_numerico = 0
        total_porcentual = 0
        
        for tipo, categorias in clasificacion.items():
            lit = len(categorias['literal'])
            num = len(categorias['numerico'])
            por = len(categorias['porcentual'])
            
            total_literal += lit
            total_numerico += num
            total_porcentual += por
            
            if lit + num + por > 0:
                modelo_nombre = {
                    'indicadorog': 'BitacoraPrincipalIndicadorOg',
                    'indicadoroe': 'BitacoraPrincipalIndicadorOE',
                    'indicadorrog': 'BitacoraPrincipalIndicadorRog',
                    'indicadorroe': 'BitacoraPrincipalIndicadorRoe'
                }.get(tipo, '')
                
                print(f"\n📌 {tipo.upper()} → {modelo_nombre}:")
                if lit > 0:
                    print(f"   • Literales (A-Z): {lit} registros")
                if num > 0:
                    print(f"   • Numéricos (1-9): {num} registros")
                if por > 0:
                    print(f"   • Porcentuales (%): {por} registros")
        
        print(f"\n📊 TOTALES GLOBALES:")
        print(f"   • Literales (A-Z): {total_literal}")
        print(f"   • Numéricos (1-9): {total_numerico}")
        print(f"   • Porcentuales (%): {total_porcentual}")
        print(f"   • TOTAL: {total_literal + total_numerico + total_porcentual}")
        
        # 6. INICIAR TRANSACCIÓN - AHORA USANDO BITÁCORAS PRINCIPALES
        print("\n" + "="*90)
        print("🔰 INICIANDO TRANSACCIÓN - INSERCIÓN EN BITÁCORAS PRINCIPALES")
        print("="*90)
        
        try:
            with transaction.atomic():
                # 6.1 Guardar informe principal
                informe = serializer.save()
                print(f"\n✅ Informe Principal {informe.id} guardado")
                
                total_insertados = 0
                
                # 6.2 Insertar Indicadores OG en Bitácora Principal
                if clasificacion['indicadorog']['literal']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorOg, 
                        'indicador_og_id',
                        clasificacion['indicadorog']['literal'], 
                        'literal',
                        informe,
                        'indicadorog',
                        usuario_obj
                    )
                if clasificacion['indicadorog']['numerico']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorOg, 
                        'indicador_og_id',
                        clasificacion['indicadorog']['numerico'], 
                        'numerico',
                        informe,
                        'indicadorog',
                        usuario_obj
                    )
                if clasificacion['indicadorog']['porcentual']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorOg, 
                        'indicador_og_id',
                        clasificacion['indicadorog']['porcentual'], 
                        'porcentual',
                        informe,
                        'indicadorog',
                        usuario_obj
                    )
                
                # 6.3 Insertar Indicadores OE en Bitácora Principal
                if clasificacion['indicadoroe']['literal']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorOE, 
                        'indicador_oe_id',
                        clasificacion['indicadoroe']['literal'], 
                        'literal',
                        informe,
                        'indicadoroe',
                        usuario_obj
                    )
                if clasificacion['indicadoroe']['numerico']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorOE, 
                        'indicador_oe_id',
                        clasificacion['indicadoroe']['numerico'], 
                        'numerico',
                        informe,
                        'indicadoroe',
                        usuario_obj
                    )
                if clasificacion['indicadoroe']['porcentual']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorOE, 
                        'indicador_oe_id',
                        clasificacion['indicadoroe']['porcentual'], 
                        'porcentual',
                        informe,
                        'indicadoroe',
                        usuario_obj
                    )
                
                # 6.4 Insertar Indicadores ROG en Bitácora Principal
                if clasificacion['indicadorrog']['literal']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorRog, 
                        'indicador_rog_id',
                        clasificacion['indicadorrog']['literal'], 
                        'literal',
                        informe,
                        'indicadorrog',
                        usuario_obj
                    )
                if clasificacion['indicadorrog']['numerico']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorRog, 
                        'indicador_rog_id',
                        clasificacion['indicadorrog']['numerico'], 
                        'numerico',
                        informe,
                        'indicadorrog',
                        usuario_obj
                    )
                if clasificacion['indicadorrog']['porcentual']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorRog, 
                        'indicador_rog_id',
                        clasificacion['indicadorrog']['porcentual'], 
                        'porcentual',
                        informe,
                        'indicadorrog',
                        usuario_obj
                    )
                
                # 6.5 Insertar Indicadores ROE en Bitácora Principal
                if clasificacion['indicadorroe']['literal']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorRoe, 
                        'indicador_roe_id',
                        clasificacion['indicadorroe']['literal'], 
                        'literal',
                        informe,
                        'indicadorroe',
                        usuario_obj
                    )
                if clasificacion['indicadorroe']['numerico']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorRoe, 
                        'indicador_roe_id',
                        clasificacion['indicadorroe']['numerico'], 
                        'numerico',
                        informe,
                        'indicadorroe',
                        usuario_obj
                    )
                if clasificacion['indicadorroe']['porcentual']:
                    total_insertados += self.insertar_bitacora_principal(
                        BitacoraPrincipalIndicadorRoe, 
                        'indicador_roe_id',
                        clasificacion['indicadorroe']['porcentual'], 
                        'porcentual',
                        informe,
                        'indicadorroe',
                        usuario_obj
                    )
                
                print(f"\n🎉 INSERCIÓN COMPLETADA: {total_insertados} registros en bitácoras PRINCIPALES")
                
                #6.6 INsertar Validadores
                print("\n" + "="*90)
                print("🔰 INSERTANDO VALIDADORES")
                print("="*90)

                total_validadores_insertados = self.insertar_validadores(
                    validadores_data,
                    informe,
                    usuario_obj
                )
                print(f"\n🎉 VALIDADORES INSERTADOS: {total_validadores_insertados} de {len(validadores_data)}")

                #6.7 Actualizar Actividad
                print("\n" + "="*90)
                print("🔰 ACTUALIZANDO ACTIVIDAD")
                print("="*90)
                actividad_actualizada = self.actualizar_actividad(informe_data)
                if actividad_actualizada:
                    print(f"\n✅ Actividad actualizada exitosamente")



        except Exception as e:
            print(f"\n❌ ERROR - Transacción revertida: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error al guardar el informe',
                'detalle': str(e)
            }, status=500)
        
        # 7. RESPONDER
        return Response({
            'success': True,
            'mensaje': 'Informe Actividad Principal creado exitosamente',
            'id': informe.id,
            'resumen': {
                'total_indicadores': total_general,
                'insertados': total_insertados,
                'por_tipo': {
                    'literales': total_literal,
                    'numericos': total_numerico,
                    'porcentuales': total_porcentual
                },
                'validadores_recibidos': len(validadores_data),
                'validadores_insertados': total_validadores_insertados,
                'actividad_actualizada': {
                    'id': actividad_actualizada.id if actividad_actualizada else None,
                    'codigo': actividad_actualizada.codigo if actividad_actualizada else None,
                    'totalReportado': str(actividad_actualizada.totalReportado) if actividad_actualizada and actividad_actualizada.totalReportado else None,
                    'totalEjecutado': str(actividad_actualizada.totalEjecutado) if actividad_actualizada and actividad_actualizada.totalEjecutado else None,
                    'saldo': str(actividad_actualizada.saldo) if actividad_actualizada and actividad_actualizada.saldo else None
                }
            }
        }, status=200)
        