from django.urls import path
from .views import *
from .viewsuser import RegisterView, LoginView, LogoutView, UserDetailView, ChangePasswordView, UsuarioListView, UsuarioDetailAdminView, UsuarioPorIdView, RegistrarUsuarioView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


router.register(r'pei', PeiViewModel, basename='pei')
# router.register(r'indicadores', IndicadorPeiViewSet, basename='indicadores')
# router.register(r'objetivos-pei', ObjetivosPeiViewModel, basename='obj.pei')
# router.register(r'indicadores-cuantitativos', IndicadorPeiCuantitativoViewSet)
# router.register(r'indicadores-cualitativos', IndicadorPeiCualitativoViewSet)
# router.register(r'factores-criticos', FactoresCriticosView, basename='factores_criticos')

#PROYECTOS
router.register(r'proyectos', ProyectoViewModel, basename='proyectos')
#Proyectos - Diagrama
router.register(r'diagramas', DiagramaEstructuraView, basename='diagrama_proyecto')
#Proyectos - Objetivo General
router.register(r'proy-obj-gral', ProyObjGralViewModel , basename='proy_obj_gral')
router.register(r'proy-obj-esp', ProyObjEspViewModel, basename='proy_obj_esp')
router.register(r'kpi', KpiViewSet, basename='kpi_proyecto')
router.register(r'instancia-gestora', ProyInstGestoraViewModel, basename='inst_gestora')
router.register(r'indicadores-og', IndicadorObjetivoGralViewset, basename='indicador_obj_gral')
router.register(r'indicador-oe', IndicadorObjetivoEspecificoViewset, basename="indicador_obj_espec")
router.register(r'indicador-resultado-oe', IndicadorResultadoOEViewset, basename='indicador_resultado_oe')
router.register(r'indicador-resultado-og', IndicadorResultadoOgViewset, basename="indicador_resultado_obj_gral")
router.register(r'resultado-og', ResultadoObjetivoGeneralViewset, basename="resultado_obj_gral")
router.register(r'resultado-oe', ResultadoObjetivoEspecificoViewset, basename="resultado_obj_espec")
router.register(r'producto-oe', ProductoOEViewset, basename='producto_obj_espec')
router.register(r'producto-result-oe', ProductoResultadoOEViewset, basename='producto_res_oe')
router.register(r'producto-general', ProductoGeneralViewset, basename='producto_general')
router.register(r'procesos', ProcesoViewset, basename='procesos')
router.register(r'actividades', ActividadViewset, basename='actividades')
router.register(r'procedencia-fondos', ProcedenciaFondosViewmodel, basename='procedencia_fondos')


urlpatterns =[
    #PEI
    path(r'pei-vigente/', obtener_pei_vigente, name='pei-vigente'),
    path(r'pei-vigente/<int:pei_id>/', establecer_pei_vigente, name='establecer-pei-vigente'),
    ######################## USUARIOS #################################
    # Autenticación
    path('usr/registrar/', RegistrarUsuarioView.as_view(), name='registrar-usuario'),
    path('usr/login/', LoginView.as_view(), name='login'),
    path('usr/logout/', LogoutView.as_view(), name='logout'),
    # Perfil de usuario
    path('usr/me/', UserDetailView.as_view(), name='user-detail'),
    path('usr/change-password/', ChangePasswordView.as_view(), name='change-password'),
    # Admin endpoints
    path('usr/usuarios/', UsuarioListView.as_view(), name='usuario-list'),
    path('usr/usuarios/<str:username>/', UsuarioDetailAdminView.as_view(), name='usuario-detail-admin'),
    path('usr/usuario/<int:id>/', UsuarioPorIdView.as_view(), name='usuario-por-id'),
]

urlpatterns += router.urls