from django.urls import path
from .views import *
from .viewsuser import RegisterView, LoginView, LogoutView, UserDetailView, ChangePasswordView, UsuarioListView, UsuarioDetailAdminView, UsuarioPorIdView, RegistrarUsuarioView
from rest_framework.routers import DefaultRouter
from .viewtarea import TareaActividadView

#PEI
router = DefaultRouter()
#PEI
router.register(r'pei', PeiViewModel, basename='pei')
router.register(r'indicadores', IndicadorPeiViewSet, basename='indicadores')
router.register(r'objetivos-pei', ObjetivosPeiViewModel, basename='obj.pei')
router.register(r'indicadores-cuantitativos', IndicadorPeiCuantitativoViewSet)
router.register(r'indicadores-cualitativos', IndicadorPeiCualitativoViewSet)
router.register(r'factores-criticos', FactoresCriticosView, basename='factores_criticos')


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
#Tareas de Actividades
router.register(r'tareas-actividad', TareaActividadView, basename='tarea-act')


urlpatterns =[
    #PEI
    path(r'pei/<int:pk>/objetivos/', PeiObjetivosIndicadoresView.as_view(), name='pei-objetivos'),
    path(r'pei/estructura/<int:id>/', PeiEstructuraCompletaView.as_view(), name='pei-estructura'),
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
    ###################### PROYECTOS ############################################
    path(r'proyectos/planificacion/<int:pei_id>/', ProyectoPlanificacionView.as_view(), name='proyectos-planificacion'  ),
    path(r'proyectos/<int:proyecto_id>/objetivo-general/', ObjetivoGeneralPorProyectoView.as_view(), name='obj-general-por-proyecto'),
    path(r'proyecto-estructura-nodos/<int:id>/', ProyectoEstructuraView.as_view(), name='proyecto-estructura' ),
    path(r'diagramas/<int:pk>/actualizar/', DiagramaEstructuraUpdateView.as_view(), name='actualizar-diagrama'),
    path(r'proyecto/<int:pk>/estructura/', ProyectoDetalladoView.as_view(), name='proyecto-id-estructura' ),
    path(r'proyectos-planificacion/', ProyectosPlanificacionList.as_view(), name='proyecto-planificacion' ),
    path(r'proyecto/<int:proyecto_id>/conteos/', conteos_proyecto, name="conteos-proyecto"),
    path(r'proyectos/<int:proyecto_id>/procesos/', ProcesosPorProyectoListView.as_view(), name='procesos-por-proyecto'),
    path(r'pei/<int:pei_id>/listobj/', SimpleObjetivosPeiListView.as_view(), name='objetivos-pei-list'),
    path(r'objetivos/<int:objetivo_id>/indicadores-compactos/',  IndicadoresCompactosView.as_view(), name='indicadores-compactos'),
    path(r'proyectos/<int:proyecto_id>/indicadores-og/', IndicadoresObjetivoGeneralView.as_view(),  name='indicadores-og'),
    path(r'proyectos/<int:proyecto_id>/objetivos-especificos/', ObjetivosEspecificosCombinadosView.as_view(),  name='objetivos-especificos-lista'),
    path(r'objetivos-especificos/<int:objetivo_id>/indicadores/', indicadores_objetivo_especifico, name='indicadores_objetivo_especifico'),
    path(r'objetivos-especificos/<int:oe_id>/productos/', productos_objetivo_especifico, name='productos_objetivo_especifico'),
    path(r'objetivos-especificos/<int:oe_id>/resultados/', resultados_objetivo_especifico, name='resultados_objetivo_especifico'),
    path(r'resultados-oe/<int:resultado_id>/indicadores/', indicadores_resultado_oe, name='indicadores_resultado_oe'),
    path(r'proyectos/<int:proyecto_id>/actividades/', ActividadesProyectoDropdownList.as_view(), name='actividades-proyecto' ),
    path(r'proyectos/<int:proyecto_id>/resultados-og/', ResultadosOGDropdownList.as_view(), name='resultados-og-dropdown'),
    path(r'resultados-og/<int:resultado_og_id>/indicadores/', IndicadoresResultadoOGDropdownList.as_view(), name='indicadores-resultado-og-dropdown'),
    path(r'proyectos/<int:proyecto_id>/indicadores-og/count/', count_indicadores_og, name='count-indicadores-og'),    
    path(r'proyectos/<int:proyecto_id>/resultados-og/count/', count_resultados_og, name='count-resultados-og'),
    path(r'proyectos/<int:proyecto_id>/column-stats/', ColumnVisibilityStatsView.as_view(), name='column-stats'),
    path(r'test/', test_endpoint, name='test-endpoint'),    
]

urlpatterns += router.urls