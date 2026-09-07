# spme/spme_gestion_acceso/services/usuarios/usuario_service.py
from ...repositories.usuarios.usuario_repository import UsuarioRepository
from ...serializers.usuario_serializer import UsuarioSolicitanteSerializer


class UsuarioService:
    
    @staticmethod
    def obtener_solicitante(id_usuario):
        usuario = UsuarioRepository.obtener_por_id(id_usuario)
        if not usuario:
            return None
        return UsuarioSolicitanteSerializer(usuario).data