"""
Script para verificar que los campos descripcion_actividad, objetivo_actividad 
y datos_forma_pago se guardan correctamente en la base de datos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from spme_monitoreo.models import SolicitudFondos

# Obtener la última solicitud creada
try:
    ultima_solicitud = SolicitudFondos.objects.latest('id')
    
    print("="*80)
    print("VERIFICACIÓN DE ÚLTIMA SOLICITUD DE FONDOS CREADA")
    print("="*80)
    print(f"\n📋 ID: {ultima_solicitud.id}")
    print(f"📝 Número de Formulario: {ultima_solicitud.numeroFormulario}")
    print(f"📍 Lugar: {ultima_solicitud.lugarSolicitud}")
    print(f"💰 Monto: {ultima_solicitud.montoSolicitado}")
    
    print("\n" + "="*80)
    print("CAMPOS QUE ESTABAN FALLANDO:")
    print("="*80)
    
    # Verificar descripcion_actividad
    print(f"\n✓ descripcion_actividad:")
    if ultima_solicitud.descripcion_actividad:
        print(f"  ✅ GUARDADO: '{ultima_solicitud.descripcion_actividad}'")
    else:
        print(f"  ❌ NULL o vacío")
    
    # Verificar objetivo_actividad
    print(f"\n✓ objetivo_actividad:")
    if ultima_solicitud.objetivo_actividad:
        print(f"  ✅ GUARDADO: '{ultima_solicitud.objetivo_actividad}'")
    else:
        print(f"  ❌ NULL o vacío")
    
    # Verificar datos_forma_pago
    print(f"\n✓ datos_forma_pago:")
    if ultima_solicitud.datos_forma_pago:
        print(f"  ✅ GUARDADO: {ultima_solicitud.datos_forma_pago}")
    else:
        print(f"  ❌ NULL o vacío")
    
    print("\n" + "="*80)
    print("OTROS CAMPOS:")
    print("="*80)
    print(f"\n✓ detalleDestinoFondos: {ultima_solicitud.detalleDestinoFondos}")
    print(f"✓ fechaSolicitud: {ultima_solicitud.fechaSolicitud}")
    print(f"✓ fechaRealizacionActividad: {ultima_solicitud.fechaRealizacionActividad}")
    print(f"✓ formaPago_id: {ultima_solicitud.formaPago_id}")
    print(f"✓ usuario_id: {ultima_solicitud.usuario_id}")
    print(f"✓ actividad_id: {ultima_solicitud.actividad_id}")
    
    print("\n" + "="*80)
    
    # Verificar si los 3 campos problemáticos están guardados
    if (ultima_solicitud.descripcion_actividad and 
        ultima_solicitud.objetivo_actividad and 
        ultima_solicitud.datos_forma_pago):
        print("\n🎉 ¡ÉXITO! Todos los campos se guardaron correctamente.")
    else:
        print("\n⚠️  ADVERTENCIA: Algunos campos no se guardaron.")
        print("   Prueba crear una nueva solicitud usando Bruno o el endpoint.")
    
except SolicitudFondos.DoesNotExist:
    print("❌ No hay solicitudes de fondos en la base de datos.")
    print("   Crea una solicitud usando Bruno para probar.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
