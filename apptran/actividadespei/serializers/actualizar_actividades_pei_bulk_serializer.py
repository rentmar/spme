# serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import json
from spme_estructuracion_pei.models import ActividadPei

class ActividadPeiBatchUpdateSerializer(serializers.ModelSerializer):
    # Campos del request
    tipo = serializers.CharField(required=False, allow_blank=True)
    responsable = serializers.CharField(required=False, allow_blank=True)  # Cambiado de responsable_id a responsable
    responsable_username = serializers.CharField(required=False, allow_blank=True)
    procedencia_fondos = serializers.JSONField(required=False, allow_null=True)
    presupuesto = serializers.CharField(required=False, allow_blank=True)
    fecha_inicio = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d', '%Y-%m-%d', ''])
    fecha_cierre = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d', '%Y-%m-%d', ''])
    
    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'supuestos', 'riesgos',
            'estado', 'tipo', 'fecha_inicio', 'fecha_cierre', 'procedencia_fondos',
            'presupuesto', 'responsable', 'responsable_username', 'gradoEjecucion'
        ]
        read_only_fields = ['id']
    
    def validate_procedencia_fondos(self, value):
        """Validar procedencia_fondos que puede ser string vacío, dict, array o null"""
        if value == "" or value is None:
            return None
        
        # Si ya es dict, list o JSON válido, retornar como está
        if isinstance(value, (dict, list)):
            return value
        
        # Si es string, intentar parsear como JSON
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Si no es JSON, podría ser un string simple
                return value
        
        # Para cualquier otro tipo, retornar None
        return None
    
    def validate_fecha_inicio(self, value):
        """Validar fecha inicio - permite strings vacíos"""
        if isinstance(value, str) and value.strip() == "":
            return None
        return value
    
    def validate_fecha_cierre(self, value):
        """Validar fecha cierre - permite strings vacíos"""
        if isinstance(value, str) and value.strip() == "":
            return None
        return value
    
    def validate_presupuesto(self, value):
        """Validar y formatear presupuesto"""
        if value == "" or value is None:
            return Decimal('0.00')
        
        try:
            # Convertir a Decimal
            if isinstance(value, str):
                # Remover símbolos de moneda si existen
                value = value.replace('$', '').replace(',', '').strip()
                if value == "":
                    return Decimal('0.00')
                return Decimal(value)
            elif isinstance(value, (int, float)):
                return Decimal(str(value))
            else:
                return Decimal('0.00')
        except (InvalidOperation, ValueError, TypeError) as e:
            print(f"Error convirtiendo presupuesto {value}: {e}")
            return Decimal('0.00')
    
    def validate_tipo(self, value):
        """Convertir string de tipo (ej: 'ACAP - Actividad de Capacitación') a instancia de TipoActividad"""
        if not value or value.strip() == "":
            return None
        
        try:
            # Extraer la sigla del tipo (ej: 'ACAP' de 'ACAP - Actividad de Capacitación')
            tipo_str = value.strip()
            
            # Si el formato es "SIGLA - Descripción", extraer la sigla
            if ' - ' in tipo_str:
                sigla = tipo_str.split(' - ')[0].strip()
            else:
                # Si solo viene la sigla o descripción, usar el string completo
                sigla = tipo_str
            
            print(f"Buscando tipo con sigla: '{sigla}' para valor: '{value}'")
            
            # Buscar el TipoActividad por sigla
            try:
                from spme_actividades.models import TipoActividad
                tipo_actividad = TipoActividad.objects.filter(sigla__iexact=sigla).first()
                
                if not tipo_actividad:
                    # Si no se encuentra por sigla exacta, buscar por sigla que contenga el texto
                    tipo_actividad = TipoActividad.objects.filter(sigla__icontains=sigla).first()
                
                if not tipo_actividad:
                    # Si aún no se encuentra, buscar por descripción
                    tipo_actividad = TipoActividad.objects.filter(tipo_actividad__icontains=tipo_str).first()
                
                if tipo_actividad:
                    print(f"Tipo encontrado: {tipo_actividad}")
                    return tipo_actividad  # Retornar la instancia
                else:
                    print(f"Tipo no encontrado para: '{sigla}'")
                    return None
                    
            except (ImportError, Exception) as e:
                print(f"Error buscando tipo: {e}")
                return None
                
        except Exception as e:
            print(f"Error procesando tipo {value}: {e}")
            return None
    
    def validate_responsable(self, value):
        """Convertir username del responsable a instancia de Usuario"""
        if not value or value.strip() == "" or value == "No asignado":
            return None
        
        try:
            from spme_autenticacion.models import Usuario
            username = value.strip()
            print(f"Buscando usuario con username: '{username}'")
            
            # Buscar usuario por username
            usuario = Usuario.objects.filter(username__iexact=username).first()
            
            if not usuario:
                print(f"Usuario no encontrado: '{username}'")
                return None
            
            print(f"Usuario encontrado: {usuario.id} - {usuario.username}")
            return usuario  # Retornar la instancia
            
        except (ImportError, Exception) as e:
            print(f"Error buscando usuario {value}: {e}")
            return None
    
    def validate(self, data):
        """Validaciones generales y transformaciones"""
        
        # Validar fechas si ambas existen
        if data.get('fecha_inicio') and data.get('fecha_cierre'):
            if data['fecha_cierre'] < data['fecha_inicio']:
                raise ValidationError({
                    'fecha_cierre': 'La fecha de cierre no puede ser anterior a la fecha de inicio'
                })
        
        # Procesar gradoEjecucion para extraer solo el código de estado
        if 'gradoEjecucion' in data:
            grado = data['gradoEjecucion']
            if grado and '-' in grado:
                # Extraer solo el código (ej: "PLAN" de "PLAN-Planificada")
                codigo_grado = grado.split('-')[0].strip()
                # Validar que el código sea válido
                codigos_validos = [codigo for codigo, _ in ActividadPei.ESTADOS_ACTIVIDAD]
                if codigo_grado in codigos_validos:
                    data['estado'] = codigo_grado
        
        # Calcular saldo si viene presupuesto
        if 'presupuesto' in data:
            presupuesto = data['presupuesto']
            
            # Obtener total ejecutado de la instancia actual
            total_ejecutado = Decimal('0.00')
            if self.instance and self.instance.totalEjecutado:
                try:
                    total_ejecutado = Decimal(str(self.instance.totalEjecutado))
                except (InvalidOperation, ValueError):
                    total_ejecutado = Decimal('0.00')
            
            # Calcular saldo
            try:
                saldo = presupuesto - total_ejecutado
                if saldo < 0:
                    saldo = Decimal('0.00')
                data['saldo'] = saldo
            except Exception as e:
                print(f"Error calculando saldo: {e}")
                data['saldo'] = presupuesto
        
        # Actualizar también el presupuestoGlobal con el mismo valor
        if 'presupuesto' in data:
            data['presupuestoGlobal'] = data['presupuesto']
        
        # Remover campos que no son del modelo antes de save
        data.pop('responsable_username', None)
        
        return data
    
    def update(self, instance, validated_data):
        """Actualizar la instancia con los datos validados"""
        
        # Log para debugging
        print(f"Actualizando actividad {instance.id} con datos: {validated_data}")
        
        # Actualizar cada campo
        for attr, value in validated_data.items():
            if attr in ['tipo', 'responsable'] and value is None:
                # Si el tipo o responsable vienen como None, mantener el valor actual
                continue
            setattr(instance, attr, value)
        
        # Guardar cambios
        instance.save()
        print(f"Actividad {instance.id} guardada exitosamente")
        return instance