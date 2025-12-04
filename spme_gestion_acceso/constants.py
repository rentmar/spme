# spme_gestion_acceso/constants.py
"""
Constantes centralizadas para el sistema de gestión de acceso
"""

class NivelesAcceso:
    """Constantes para niveles de acceso"""
    SIN_ACCESO = 0
    LECTURA = 1
    EDICION = 2
    ADMINISTRACION = 3
    
    CHOICES = [
        (SIN_ACCESO, 'Sin acceso'),
        (LECTURA, 'Solo lectura'),
        (EDICION, 'Edicion'),
        (ADMINISTRACION, 'Administracion')
    ]
    
    NOMBRES = {
        SIN_ACCESO: 'Sin acceso',
        LECTURA: 'Solo lectura',
        EDICION: 'Edicion',
        ADMINISTRACION: 'Administracion'
    }


class CacheKeys:
    """Constantes para claves de cache"""
    PREFIX = 'permisos'
    
    @classmethod
    def instancias_usuario(cls, usuario_id):
        return f'{cls.PREFIX}:usuario:{usuario_id}:instancias'
    
    @classmethod
    def proyecto_usuario(cls, usuario_id, proyecto_id):
        return f'{cls.PREFIX}:usuario:{usuario_id}:proyecto:{proyecto_id}'
    
    @classmethod
    def proyectos_usuario(cls, usuario_id):
        return f'{cls.PREFIX}:usuario:{usuario_id}:proyectos'


class Configuracion:
    """Configuraciones del sistema"""
    CACHE_TIMEOUT = 300  # 5 minutos
    PAGE_SIZE_DEFAULT = 20
    PAGE_SIZE_MAX = 100

