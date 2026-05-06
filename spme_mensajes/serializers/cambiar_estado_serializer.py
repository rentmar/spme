#serializers/cambiar_estado_serializer.py
from rest_framework import serializers
from django.utils import timezone
from ..models import MensajeUsuario, EstadoMensaje

class CambiarEstadoMensajesSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="Lista de IDs de mensajes"
    )
    estado = serializers.ChoiceField(
        choices=EstadoMensaje.choices,
        help_text="Nuevo estado: no_leido, leido, archivado, eliminado"
    )

    def validate_ids(self, value):
        user = self.context['request'].user
        
        mensajes_existentes = MensajeUsuario.objects.filter(
            id__in=value,
            destinatario=user
        ).values_list('id', flat=True)
        
        ids_existentes = set(mensajes_existentes)
        ids_solicitados = set(value)
        ids_no_encontrados = ids_solicitados - ids_existentes
        
        if ids_no_encontrados:
            raise serializers.ValidationError(
                f"Mensajes no encontrados: {list(ids_no_encontrados)}"
            )
        
        return value

    def save(self):
        ids = self.validated_data['ids']
        estado = self.validated_data['estado']
        user = self.context['request'].user
        
        mensajes = MensajeUsuario.objects.filter(id__in=ids, destinatario=user)
        actualizados = []
        
        for mensaje in mensajes:
            # Usar los métodos del modelo si existen
            if estado == 'leido':
                mensaje.marcar_como_leido(commit=False)
            elif estado == 'no_leido':
                mensaje.marcar_como_no_leido(commit=False)
            elif estado == 'archivado':
                mensaje.archivar(commit=False)
            elif estado == 'eliminado':
                mensaje.eliminar(commit=False)
            else:
                mensaje.estado = estado
            
            mensaje.save()
            actualizados.append(mensaje.id)
        
        return {
            'mensaje': f'{len(actualizados)} mensajes actualizados',
            'actualizados': len(actualizados),
            'ids': actualizados,
            'estado': estado,
            'estado_display': EstadoMensaje(estado).label
        }