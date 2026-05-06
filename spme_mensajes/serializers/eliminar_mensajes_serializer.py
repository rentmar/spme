# serializers/eliminar_mensajes_serializer.py
from rest_framework import serializers
from ..models import MensajeUsuario

class MensajeEliminarSerializer(serializers.Serializer):
    """Serializer para eliminar múltiples mensajes"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="Lista de IDs de mensajes a eliminar"
    )
    tipo_eliminacion = serializers.ChoiceField(
        choices=[('soft', 'Soft Delete'), ('hard', 'Hard Delete')],
        required=False,
        default='soft',
        help_text="'soft' para marcar como eliminado, 'hard' para borrar permanentemente"
    )

    def validate_ids(self, value):
        """Verifica que los IDs existan y pertenezcan al usuario"""
        user = self.context['request'].user
        
        # Verificar que existan mensajes con esos IDs para este usuario
        mensajes_existentes = MensajeUsuario.objects.filter(
            id__in=value,
            destinatario=user
        ).values_list('id', flat=True)
        
        ids_existentes = set(mensajes_existentes)
        ids_solicitados = set(value)
        
        # Verificar si hay IDs que no existen o no pertenecen al usuario
        ids_no_encontrados = ids_solicitados - ids_existentes
        
        if ids_no_encontrados:
            raise serializers.ValidationError(
                f"No se encontraron los siguientes mensajes o no tienes permiso: {list(ids_no_encontrados)}"
            )
        
        return value

    def save(self):
        """Elimina los mensajes"""
        ids = self.validated_data['ids']
        tipo_eliminacion = self.validated_data['tipo_eliminacion']
        user = self.context['request'].user
        
        # Filtrar mensajes del usuario
        mensajes = MensajeUsuario.objects.filter(
            id__in=ids,
            destinatario=user
        )
        
        if tipo_eliminacion == 'hard':
            # Eliminación permanente
            count = mensajes.count()
            mensajes.delete()
            mensaje_accion = f"{count} mensajes eliminados permanentemente"
        else:
            # Soft delete
            count = 0
            for mensaje in mensajes:
                mensaje.eliminar(commit=True)
                count += 1
            mensaje_accion = f"{count} mensajes marcados como eliminados"
        
        return {
            'mensaje': mensaje_accion,
            'eliminados': count,
            'tipo_eliminacion': tipo_eliminacion,
            'ids': ids
        }