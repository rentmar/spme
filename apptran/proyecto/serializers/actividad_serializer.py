# serializers.py
from rest_framework import serializers
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad, TipoActividad


class TipoActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActividad
        fields = ['id', 'sigla', 'tipo_actividad']


class TareaActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = ['id', 'codigo', 'titulo', 'descripcion', 'estado', 'fecha_limite']


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'correo', 'nombre', 'paterno']


class ActividadSerializer(serializers.ModelSerializer):
    tipo = TipoActividadSerializer(read_only=True)
    tareas = TareaActividadSerializer(many=True, read_only=True)
    proyecto = serializers.SerializerMethodField()
    responsable = UsuarioSerializer(read_only=True)

    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion',
            'tipo', 'tareas', 'proyecto', 'responsable',
            'estado', 'presupuesto'
        ]

    def get_proyecto(self, obj):
        if not obj.proyecto:
            return None
        
        proyecto = obj.proyecto
        return {
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'titulo': proyecto.titulo,
            'instancias_gestoras': list(
                proyecto.instancia_gestora.values('id', 'codigo', 'instancia')
            ),
            'procedencia_fondos': list(
                proyecto.procedencia_fondos.values('id', 'sigla', 'financiera')
            )
        }