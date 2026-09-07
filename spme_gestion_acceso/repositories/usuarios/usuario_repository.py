# spme/spme_gestion_acceso/repositories/usuarios/usuario_repository.py
from spme_autenticacion.models import Usuario

class UsuarioRepository:
    @staticmethod
    def obtener_por_id(id_usuario):
        try:
            return Usuario.objects.get(id=id_usuario, is_active=True)
        except Usuario.DoesNotExist:
            return None

