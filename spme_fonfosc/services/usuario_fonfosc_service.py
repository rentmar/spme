# spme/spme_fonfosc/services/usuario_fonfosc_service.py

from spme_fonfosc.repositories.usuario_fonfosc_repository import UsuarioFonFoscRepository
from spme_fonfosc.serializers.usuario_fonfosc_serializer import (
    RegistroUsuarioFonFoscSerializer,
    UsuarioFonFoscSerializer,
)


class UsuarioFonFoscService:
    """Servicio para la lógica de negocio de UsuarioFonFosc"""

    @staticmethod
    def verificar_username(username):
        """Verifica disponibilidad de username"""
        disponible = UsuarioFonFoscRepository.verificar_username(username)
        return {'disponible': disponible}

    @staticmethod
    def registrar_usuario(datos):
        """
        Registra un nuevo usuario FONFOSC
        
        Args:
            datos (dict): Datos del formulario de registro
        
        Returns:
            dict: Datos del usuario creado
        """
        # Validar datos
        serializer = RegistroUsuarioFonFoscSerializer(data=datos)
        serializer.is_valid(raise_exception=True)

        # Crear usuario
        usuario_fonfosc = UsuarioFonFoscRepository.crear_usuario_fonfosc(
            serializer.validated_data
        )

        # Serializar respuesta
        return UsuarioFonFoscSerializer(usuario_fonfosc).data