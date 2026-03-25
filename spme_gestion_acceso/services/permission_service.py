# spme_gestion_acceso/services/permission_service.py
from django.utils import timezone
from django.core.cache import cache
from django.db import models
from ..models import UserInstanciaGestora, PermisoProyectoEspecifico
from ..constants import NivelesAcceso, CacheKeys, Configuracion  

class PermissionService:
    # ✅ USAR constantes centralizadas
    SIN_ACCESO = NivelesAcceso.SIN_ACCESO
    LECTURA = NivelesAcceso.LECTURA
    EDICION = NivelesAcceso.EDICION
    ADMINISTRACION = NivelesAcceso.ADMINISTRACION
    
    def __init__(self):
        self.cache_timeout = Configuracion.CACHE_TIMEOUT
    
    # ❌ ELIMINAR métodos de generación de cache keys
    # def _get_cache_key(self, usuario_id, tipo='instancias'):
    #     return f'permisos:{usuario_id}:{tipo}'
    
    def obtener_instancias_gestoras_usuario(self, usuario):
        """Obtiene las instancias gestoras del usuario con cache"""
        # ✅ USAR constantes de cache
        cache_key = CacheKeys.instancias_usuario(usuario.id)
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        instancias = UserInstanciaGestora.objects.filter(
            usuario=usuario, activo=True
        ).select_related('instancia_gestora')
        
        cache.set(cache_key, instancias, self.cache_timeout)
        return instancias
    
    def _obtener_instancias_del_proyecto(self, proyecto):
        """Obtiene las instancias gestoras de un proyecto"""
        return proyecto.instancia_gestora.values_list('id', flat=True)
    
    def tiene_acceso_proyecto(self, usuario, proyecto):
        """Verifica si el usuario tiene acceso a un proyecto específico"""
        if getattr(usuario, 'is_superuser', False):
            return True, self.ADMINISTRACION
            
        # ✅ USAR constantes de cache
        cache_key = CacheKeys.proyecto_usuario(usuario.id, proyecto.id)
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached['acceso'], cached['nivel']
        
        instancias_usuario = self.obtener_instancias_gestoras_usuario(usuario)
        instancias_proyecto_ids = self._obtener_instancias_del_proyecto(proyecto)
        
        nivel_mas_alto = self.SIN_ACCESO
        for user_instancia in instancias_usuario:
            if user_instancia.instancia_gestora_id in instancias_proyecto_ids:
                if user_instancia.nivel_acceso > nivel_mas_alto:
                    nivel_mas_alto = user_instancia.nivel_acceso
        
        if nivel_mas_alto > self.SIN_ACCESO:
            resultado = (True, nivel_mas_alto)
            cache.set(cache_key, {'acceso': True, 'nivel': nivel_mas_alto}, self.cache_timeout)
            return resultado
            
        permiso_especifico = PermisoProyectoEspecifico.objects.filter(
            usuario=usuario, proyecto=proyecto, activo=True
        ).first()
        
        if permiso_especifico:
            #Verificar si no expiro
            if permiso_especifico.fecha_expiracion and permiso_especifico.fecha_expiracion < timezone.now():
                #Ha Expirado
                resultado = (False, self.SIN_ACCESO)
                cache.set(cache_key, {'acceso': False, 'nivel': self.SIN_ACCESO}, self.cache_timeout)
                return resultado

            resultado = (True, permiso_especifico.tipo_acceso)
            cache.set(cache_key, {'acceso': True, 'nivel': permiso_especifico.tipo_acceso}, self.cache_timeout)
            return resultado
            
        resultado = (False, self.SIN_ACCESO)
        cache.set(cache_key, {'acceso': False, 'nivel': self.SIN_ACCESO}, self.cache_timeout)
        return resultado
    
    def obtener_proyectos_accesibles(self, usuario, nivel_minimo=None):
        from spme_estructuracion_proyecto.models import Proyecto
        
        if getattr(usuario, 'is_superuser', False):
            return Proyecto.objects.all().prefetch_related('instancia_gestora')
            
        if nivel_minimo is None:
            nivel_minimo = self.LECTURA

        #Proyectos por instancia gestora    
        instancias_usuario = self.obtener_instancias_gestoras_usuario(usuario)
        instancias_con_nivel_suficiente = [
            ui.instancia_gestora_id for ui in instancias_usuario 
            if ui.nivel_acceso >= nivel_minimo
        ]
        
        proyectos_por_instancia = Proyecto.objects.filter(
            instancia_gestora__in=instancias_con_nivel_suficiente
        ).prefetch_related('instancia_gestora').distinct()

        # 2. Proyectos por permisos especificos
        from django.utils import timezone
        
        #Obtener permisos activos con nivel suficiente
        permisos_activos = PermisoProyectoEspecifico.objects.filter(
            usuario=usuario, 
            activo=True, 
            tipo_acceso__gte=nivel_minimo
        )

        #Excluir permisos que ya expiraron
        # NO excluir todos los que tienen fecha (fecha_expiracion__isnull=False)
        permisos_activos = permisos_activos.exclude(
            fecha_expiracion__lt=timezone.now() 
        )
        # Los permisos con fecha_expiracion=None (sin fecha) se incluyen automáticamente
        # Los permisos con fecha futura (fecha_expiracion > now) también se incluyen
        proyectos_por_permiso = Proyecto.objects.filter(
            permisos_usuarios_especificos__in=permisos_activos
        ).prefetch_related('instancia_gestora').distinct()
        
        return (proyectos_por_instancia | proyectos_por_permiso).distinct()
    
    def obtener_nivel_acceso_proyecto(self, usuario, proyecto):
        acceso, nivel = self.tiene_acceso_proyecto(usuario, proyecto)
        return nivel if acceso else self.SIN_ACCESO
    
    def puede_ver_proyecto(self, usuario, proyecto):
        acceso, nivel = self.tiene_acceso_proyecto(usuario, proyecto)
        return acceso and nivel >= self.LECTURA
    
    def puede_editar_proyecto(self, usuario, proyecto):
        acceso, nivel = self.tiene_acceso_proyecto(usuario, proyecto)
        return acceso and nivel >= self.EDICION
    
    def puede_administrar_proyecto(self, usuario, proyecto):
        acceso, nivel = self.tiene_acceso_proyecto(usuario, proyecto)
        return acceso and nivel >= self.ADMINISTRACION
    
    def obtener_nombre_nivel_acceso(self, nivel):
        # ✅ USAR constantes centralizadas
        return NivelesAcceso.NOMBRES.get(nivel, 'Desconocido')
    
    def invalidar_cache_usuario(self, usuario_id):
        """Invalidar cache cuando cambian los permisos"""
        # ✅ USAR constantes de cache
        cache_keys = [
            CacheKeys.instancias_usuario(usuario_id),
            CacheKeys.proyectos_usuario(usuario_id),
        ]
        
        # También invalidar cache de proyectos específicos
        # Esto requiere una consulta, pero es necesaria para consistencia
        proyectos_usuario = PermisoProyectoEspecifico.objects.filter(
            usuario_id=usuario_id
        ).values_list('proyecto_id', flat=True)
        
        for proyecto_id in proyectos_usuario:
            cache_keys.append(CacheKeys.proyecto_usuario(usuario_id, proyecto_id))
        
        cache.delete_many(cache_keys)