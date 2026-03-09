#Views
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from spme_monitoreo.models import (InformeTareaPrincipal)
from spme_proyectos_reportes.models import (
    # Modelos PRINCIPALES
    BitacoraPrincipalIndicadorOg,
    BitacoraPrincipalIndicadorOE,
    BitacoraPrincipalIndicadorRog,
    BitacoraPrincipalIndicadorRoe
)
from spme_autenticacion.models import Usuario
from ..serializers.crear_informe_tarea_principal_serializer import InformeTareaPrincipalSerializer
from datetime import datetime


class CrearInformeTareaView(APIView):
    """
    Endpoint para crear informes de tareas con transacciones
    INSERTA EN BITACORAS PRINCIPALES
    """

    #=================================
    #METODO POST
    #=================================
    def post(self, request):
        #Obtener el usuario
        usuario_id = request.data.get('usuario')
        usuario_obj = None
        #Si hay id de usuario obtener el objeto
        if usuario_id:
            try:
                usuario_obj = Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                print(f"⚠️ Usuario con ID {usuario_id} no encontrado")    

        #1.Validar el serializer
        serializer = InformeTareaPrincipalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errores': serializer.errors}, 
                status=400)
        
        #2. Extraer indicadores
        indicadores = request.data.get('avanceIndicadores')
        if indicadores is None:
            indicadores = {}
        print("\n" + "="*90)
        print("🔍 PROCESO DE VERIFICACIÓN DE INDICADORES (BITÁCORAS PRINCIPALES)")
        print("="*90)
        
        #3. PRIMERA COMPROBACION: Tipos de indicadores
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
            #Mapeado de los indicadores
            modelo_destino = {
                'indicadorog': 'BitacoraPrincipalIndicadorOg',
                'indicadoroe': 'BitacoraPrincipalIndicadorOE',
                'indicadorrog': 'BitacoraPrincipalIndicadorRog',
                'indicadorroe': 'BitacoraPrincipalIndicadorRoe'
            }.get(tipo, 'Desconocido')
            print(f"   • {tipo}: {cantidad} registro(s) - {'✅ EXISTE' if cantidad > 0 else '❌ VACÍO'} → {modelo_destino}")
        
        print(f"\n   📌 TOTAL GENERAL: {total_general} indicadores")

        #4. SEGUNDA COMPROBACION: Por cada tipo, verificar el tipo de dato de cada registro
        print("\n" + "="*90)
        print("🔍 SEGUNDA COMPROBACIÓN - TIPO DE DATO POR REGISTRO")
        print("="*90)

        #Estructura para guardar la clasificacion por cada tipo de dato
        clasificacion = {
            'indicadorog': {'literal': [], 'numerico': [], 'porcentual': []},
            'indicadoroe': {'literal': [], 'numerico': [], 'porcentual': []},
            'indicadorrog': {'literal': [], 'numerico': [], 'porcentual': []},
            'indicadorroe': {'literal': [], 'numerico': [], 'porcentual': []}
        }

        #Clasificacion de los indicadores
        for tipo, lista in tipos_indicadores.items():

            if not lista:
                print(f"\n📌 {tipo.upper()}: Sin registros")
                continue

            print(f"\n📌 {tipo.upper()} ({len(lista)} registros):")

            for i, item in enumerate(lista):
                tipo_dato = item.get('tipo_dato')
                id_indicador = item.get('id_indicador')

                #Clasificar segun el tipo de dato
                if tipo_dato == 'A-Z':
                    categoria = 'literal'
                    valor = item.get('valor_literal')
                elif tipo_dato == '%':
                    categoria = 'porcentual'
                    valor = item.get('valor_porcentual')
                else:  # '1-9'
                    categoria = 'numerico'
                    valor = item.get('valor_numerico')

                #Guardar en clasificacion
                clasificacion[tipo][categoria].append({
                        'id_indicador': id_indicador,
                        'fecha_registro': item.get('fecha_registro'),
                        'valor': valor,
                        'observaciones': item.get('observaciones'),
                        'timestamp_registro': item.get('timestamp_registro'),
                        'registro_completo': item
                        # 'registrado_por' ELIMINADO - no existe en el modelo
                    })    

                #Mostrar clasificacion
                print(f"   {i+1}. ID {id_indicador} → Tipo: {tipo_dato} ({categoria}) = {valor}")

        #5. Resumen de la clasificacion
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
                #6.1 Guardar Informe principal
                informe = serializer.save()
                print(f"\n✅ Informe Principal {informe.id} guardado")

                total_insertados = 0

                #6.2 Insertar Indicadores OG en bitacora principal
                # Literales OG
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

                # Numéricos OG
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

                # Porcentuales OG
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

                #6.3 Insertar Indicadores OE en bitacora principal
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
                
                #6.4 Insertar Indicadores ROG en bitacora principal
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
                
                 #6.5 Insertar Indicadores ROE en bitacora principal
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

        except Exception as e:
            print(f"\n❌ ERROR - Transacción revertida: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error al guardar el informe',
                'detalle': str(e)
            }, status=500)

        #7. Responder
        return Response({
            'success': True,
            'mensaje': 'Informe de Tarea Principal creado exitosamente',
            'id informe tarea': informe.id,
            'resumen': {
                'total_indicadores': total_general,
                'insertados': total_insertados,
                'por_tipo': {
                    'literales': total_literal,
                    'numericos': total_numerico,
                    'porcentuales': total_porcentual
                }
            }
        }, status=200)
    
    # ============================================
    # MÉTODO AUXILIAR - Insertar en bitácora principal
    # ============================================
    def insertar_bitacora_principal(self, modelo, campo_fk, registros, tipo_dato_categoria, informe, tipo_indicador_valor, usuario=None):
        """
        Inserta registros en la bitácora PRINCIPAL correspondiente
        tipo_indicador_valor: 'indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe'
        AHORA INCLUYE: usuario_registro (objeto Usuario) y snapshot_indicador
        """
        if not registros:
            return 0
        
        print(f"\n   📝 Insertando en {modelo.__name__} ({len(registros)} {tipo_dato_categoria}):")
        count = 0

        for reg in registros:
            #Validar que tenga el id_indicador
            if not reg.get('id_indicador'):
                print(f"      ❌ Registro sin id_indicador: {reg}")
                continue

            #Determinar el tipo de dato segun la categoria
            if tipo_dato_categoria == 'literal':
                tipo_dato = 'A-Z'
            elif tipo_dato_categoria == 'porcentual':
                tipo_dato = '%'
            else:  # numerico
                tipo_dato = '1-9'

            # Construir kwargs con TODOS los campos necesarios
            kwargs = {
                campo_fk: reg['id_indicador'],
                'tipo_indicador': tipo_indicador_valor,  # ← CAMPO OBLIGATORIO
                'fecha_registro': reg['fecha_registro'],
                'tipo_dato': tipo_dato,
                'observaciones': reg.get('observaciones', ''),
                'timestamp_registro': reg.get('timestamp_registro'),
                'informe_tarea': informe,
                'usuario_registro': usuario,
                'snapshot_indicador': reg.get('registro_completo', reg),
            }

            # Asignar el valor según el tipo de dato
            if tipo_dato_categoria == 'literal':
                kwargs['valor_literal'] = reg['valor']
            elif tipo_dato_categoria == 'numerico':
                kwargs['valor_numerico'] = reg['valor']
            else:  # porcentual
                kwargs['valor_porcentual'] = reg['valor']

            #Crear el registro
            try:
                modelo.objects.create(**kwargs)
                count += 1
                print(f"      ✅ ID {reg['id_indicador']} ({tipo_dato_categoria}) - usuario: {usuario.username if usuario else 'None'}")
            except Exception as e:
                print(f"      ❌ Error insertando {reg['id_indicador']}: {e}")
                raise  # Re-lanzar para que la transacción haga rollback            


        return count