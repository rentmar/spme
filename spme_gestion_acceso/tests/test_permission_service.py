from django.test import TestCase
from spme_autenticacion.models import Usuario, InstanciaGestora
from spme_estructuracion_proyecto.models import Proyecto
from ..models import UserInstanciaGestora, PermisoProyectoEspecifico
from ..services.permission_service import PermissionService

class PermissionServiceTest(TestCase):
    def setUp(self):
        self.perm_service = PermissionService()
        
        # ✅ CREANDO usuario con el modelo personalizado Usuario
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            nombre='Test',
            paterno='User',
            materno='Demo',
            ci='1234567',
            cargo='Analista',
            permisos='basico'
        )
        
        self.superuser = Usuario.objects.create_superuser(
            username='admin',
            password='adminpass123',
            nombre='Admin',
            paterno='User',
            materno='System',
            ci='7654321',
            cargo='Administrador',
            permisos='total'
        )
        
        self.instancia = InstanciaGestora.objects.create(
            codigo='TEST', 
            instancia='Instancia de Test'
        )
        self.proyecto = Proyecto.objects.create(
            codigo='PROY-TEST',
            titulo='Proyecto de Test'
        )
        self.proyecto.instancia_gestora.add(self.instancia)
        
    def test_superuser_tiene_acceso_completo(self):
        """Verificar que superuser tiene acceso completo a todos los proyectos"""
        acceso, nivel = self.perm_service.tiene_acceso_proyecto(self.superuser, self.proyecto)
        
        self.assertTrue(acceso)
        self.assertEqual(nivel, self.perm_service.ADMINISTRACION)
        self.assertTrue(self.perm_service.puede_ver_proyecto(self.superuser, self.proyecto))
        self.assertTrue(self.perm_service.puede_editar_proyecto(self.superuser, self.proyecto))
        self.assertTrue(self.perm_service.puede_administrar_proyecto(self.superuser, self.proyecto))
    
    def test_usuario_normal_sin_acceso(self):
        """Verificar que usuario normal sin instancias no tiene acceso"""
        acceso, nivel = self.perm_service.tiene_acceso_proyecto(self.user, self.proyecto)
        
        self.assertFalse(acceso)
        self.assertEqual(nivel, self.perm_service.SIN_ACCESO)
        self.assertFalse(self.perm_service.puede_ver_proyecto(self.user, self.proyecto))
    
    def test_usuario_con_instancia_lectura(self):
        """Verificar acceso con nivel de lectura"""
        UserInstanciaGestora.objects.create(
            usuario=self.user,
            instancia_gestora=self.instancia,
            nivel_acceso=self.perm_service.LECTURA
        )
        
        acceso, nivel = self.perm_service.tiene_acceso_proyecto(self.user, self.proyecto)
        
        self.assertTrue(acceso)
        self.assertEqual(nivel, self.perm_service.LECTURA)
        self.assertTrue(self.perm_service.puede_ver_proyecto(self.user, self.proyecto))
        self.assertFalse(self.perm_service.puede_editar_proyecto(self.user, self.proyecto))
        self.assertFalse(self.perm_service.puede_administrar_proyecto(self.user, self.proyecto))
    
    def test_usuario_con_instancia_edicion(self):
        """Verificar acceso con nivel de edición"""
        UserInstanciaGestora.objects.create(
            usuario=self.user,
            instancia_gestora=self.instancia,
            nivel_acceso=self.perm_service.EDICION
        )
        
        acceso, nivel = self.perm_service.tiene_acceso_proyecto(self.user, self.proyecto)
        
        self.assertTrue(acceso)
        self.assertEqual(nivel, self.perm_service.EDICION)
        self.assertTrue(self.perm_service.puede_ver_proyecto(self.user, self.proyecto))
        self.assertTrue(self.perm_service.puede_editar_proyecto(self.user, self.proyecto))
        self.assertFalse(self.perm_service.puede_administrar_proyecto(self.user, self.proyecto))
    
    def test_obtener_permisos_usuario_completo(self):
        """Verificar que se obtiene información completa de permisos"""
        UserInstanciaGestora.objects.create(
            usuario=self.user,
            instancia_gestora=self.instancia,
            nivel_acceso=self.perm_service.EDICION
        )
        
        permisos = self.perm_service.obtener_permisos_usuario_completo(self.user)
        
        self.assertEqual(permisos['user']['username'], 'testuser')
        self.assertEqual(permisos['user']['nombre_completo'], 'Test User Demo')
        self.assertFalse(permisos['user']['is_superuser'])
        self.assertEqual(len(permisos['instancias_gestoras']), 1)
        self.assertEqual(len(permisos['proyectos_accesibles']), 1)
        self.assertEqual(permisos['proyectos_accesibles'][0]['nivel_acceso'], self.perm_service.EDICION)
    
    def test_obtener_proyectos_accesibles(self):
        """Verificar que se obtienen solo proyectos accesibles"""
        UserInstanciaGestora.objects.create(
            usuario=self.user,
            instancia_gestora=self.instancia,
            nivel_acceso=self.perm_service.LECTURA
        )
        
        # Crear otro proyecto no accesible
        proyecto_no_accesible = Proyecto.objects.create(
            codigo='PROY-NO-ACC',
            titulo='Proyecto No Accesible'
        )
        
        proyectos_accesibles = self.perm_service.obtener_proyectos_accesibles(self.user)
        
        self.assertEqual(proyectos_accesibles.count(), 1)
        self.assertEqual(proyectos_accesibles.first().codigo, 'PROY-TEST')
        self.assertNotIn(proyecto_no_accesible, proyectos_accesibles)