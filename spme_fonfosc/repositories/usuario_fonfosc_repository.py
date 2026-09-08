# spme/spme_fonfosc/repositories/usuario_fonfosc_repository.py
# repositories/usuario_fonfosc_repository.py

from django.db import transaction

from spme_autenticacion.models import Usuario
from spme_fonfosc.models import UsuarioFonFosc, Institucion


class UsuarioFonFoscRepository:
    """Repositorio para UsuarioFonFosc"""

    @staticmethod
    def verificar_username(username):
        """Verifica si un username está disponible"""
        return not Usuario.objects.filter(username=username).exists()

    @staticmethod
    @transaction.atomic
    def crear_usuario_fonfosc(datos):
        """
        Crea un Usuario y su perfil UsuarioFonFosc
        
        Args:
            datos (dict): Diccionario con los datos del usuario
        
        Returns:
            UsuarioFonFosc: Instancia creada
        """
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username=datos.get('username'),
            password=datos.get('password'),
            nombre=datos.get('nombre', ''),
            paterno=datos.get('paterno', ''),
            materno=datos.get('materno', ''),
            ci=datos.get('ci', ''),
            correo=datos.get('correo', ''),
            cargo=datos.get('cargo', 'fonfosc'),
        )   

        # Obtener institución
        institucion = Institucion.objects.get(id=datos.get('institucion_id'))

        # Crear perfil FONFOSC
        usuario_fonfosc = UsuarioFonFosc.objects.create(
            usuario=usuario,
            institucion=institucion,
            telefono=datos.get('telefono', ''),
        )

        return usuario_fonfosc