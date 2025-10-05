from django.urls import path
from .views import *
from .viewsuser import RegisterView, LoginView, LogoutView, UserDetailView, ChangePasswordView, UsuarioListView, UsuarioDetailAdminView, UsuarioPorIdView, RegistrarUsuarioView, UserListNicksViews
from rest_framework.routers import DefaultRouter
from .viewtarea import TareaActividadView
from .viewmonitoreo import *
from .viewefecto import EfectoProyectoView
#Actividad y planificacion
from .viewactividad import actividades_por_proyecto
from .viewtipoactividad import TipoActividadView
from .viewslistasencillanicks import lista_nicks_usuarios
from .viewactividadbulk import procesar_actividades_bulk
from .viewsplanificacion import obtener_historial_planificacion, obtener_planificacion_version, contar_planificaciones
from .viewsactividadestareas import ActividadConTareasListView, ActividadConTareasDetailView
from .planificacion.views.viewsactividadplansegbulk import procesar_actividades_planificacion_bulk
from .actividades.views.actividad_indicador_views import ActividadIndicadorViewSet
from .actividades.views.lista_actividad_tarea_views import ActividadSubActividadViewSet
from .actividades.views.tarea_detalles_porid_views import obtener_tarea_detalle

#from planificacion.vistas.viewsrutas import PruebaPlanificacionView
from .actividades.views.viewsactividadrutas import rutas_actividad, ruta_actividad_proyecto
from .actividades.views.viewsactividadrutaindicador import obtener_ruta_actividad_con_indicadores
from .actividades.views.viewsactividadindicadorrutasposibles import rutas_actividad_indicadores
from .pei.views.viewsobjetivoindicadorpei import ObjetivoPeiPorPeiListView, IndicadorPeiPorPeiListView
#Monitoreo
from .monitoreo.views.viewssolicitudfondos import SolicitudFondosViewSet
from .monitoreo.views.viewscrearsolicitudfondos import crear_solicitud_fondos
from .monitoreo.views.viewobtenersolicitudviaje import solicitud_viaje_list, solicitud_viaje_detail
from .monitoreo.views.viewscrearsolicitudviaje import crear_solicitud_viaje
from .monitoreo.views.viewobtenerdatosform import obtener_datos_solicitud_fondos
from .monitoreo.views.crear_rendicion_cuentas_views import crear_rendicion_cuentas
from .monitoreo.views.info_rendicion_cuentas_views import RendicionCuentasDatosView
from .monitoreo.views.informe_actividad_views import InformeActividadVersionMView
#PEI
from .pei.views.viewsfactorescriticosporpei import factores_criticos_por_pei
#Proyecto
from .viewdiagramaporidproyecto import DiagramaPorProyectoView
#Informe de actividad
from .monitoreo.views.crear_informe_actividad_views import InformeActividadView
from .monitoreo.views.informe_tarea_views import crear_informe_tarea
from .monitoreo.views.informe_tarea_views import listar_informes_tarea
from .monitoreo.views.informe_tarea_views import obtener_informe_tarea
from .monitoreo.views.informe_tarea_views import actualizar_informe_tarea
from .monitoreo.views.informe_tarea_views import eliminar_informe_tarea
#Gannt
from .actividades.views.datos_gantt_views import actividades_con_estados



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
router.register(r'efectos-proyecto', EfectoProyectoView, basename='efectos_proyecto')
#Tipos de Actividad
router.register(r'tipo-actividad', TipoActividadView, basename='tipo_actividad')
#Lista de actividades
router.register(r'actividades-tareas-lista', ActividadSubActividadViewSet, basename='lista_actividades_tareas')
#Tareas de Actividades
router.register(r'tareas-actividad', TareaActividadView, basename='tareas-actividades')
#Actividad indicadores - bitacora
router.register(r'actividad-indicadores-proyecto', ActividadIndicadorViewSet, basename='actividad_indicadores_proyecto' )
#Monitoreo
router.register(r'forma-de-pago', FormaPagoView, basename='forma_de_pago')
router.register(r'solicitud-fondos', SolicitudFondosViewSet , basename='solicitud_fondos')
router.register(r'rendicion-cuentas', RendicionCuentasView, basename='rendicion_cuentas')
router.register(r'solicitud-reembolso', SolicitudReembolsoView, basename='solicitud_reembolso')
router.register(r'solicitud-viaje', SolicitudViajeView, basename='solicitud_viaje')
router.register(r'solicitud-pago-directo', SolicitudPagoDirectoView, basename='sol_pago_directo')
router.register(r'informe-actividad', InformeActividadView, basename='informe-actividades')
router.register(r'informe-de-actividad', InformeActividadVersionMView, basename='informe_de_actividad')


urlpatterns =[
    #PEI
    path(r'pei/<int:pk>/objetivos/', PeiObjetivosIndicadoresView.as_view(), name='pei-objetivos'),
    path(r'pei/estructura/<int:id>/', PeiEstructuraCompletaView.as_view(), name='pei-estructura'),
    path(r'pei-vigente/', obtener_pei_vigente, name='pei-vigente'),
    path(r'pei-vigente/<int:pei_id>/', establecer_pei_vigente, name='establecer-pei-vigente'),
    path(r'pei/<int:pei_id>/factores-criticos/', factores_criticos_por_pei,name='pei-lista-fac-criticos'),
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
    path(r'proyectos/diagrama/<int:proyecto_id>/', DiagramaPorProyectoView.as_view(), name='diagrama-de-un.proyecto'),
    path(r'test/', test_endpoint, name='test-endpoint'),   
    #Actividades y planificacion
    path(r'actividades/proyecto/<int:proyecto_id>/', actividades_por_proyecto, name='actividades_por_proyecto'), 
    path(r'usuariosnick/', UserListNicksViews.as_view(), name='lista_nicks' ),
    path(r'usuarios/lista-nicks/', lista_nicks_usuarios, name='lista-nicks-usuarios'),
    #Actividades
    path(r'actividades/procesar-bulk/<int:idproyecto>/', procesar_actividades_bulk, name='procesar_actividades_bulk'),
    path(r'actividades/historial-planificacion/<int:idproyecto>/', obtener_historial_planificacion, name='historial_planificacion'),
    path(r'actividades/planificacion/<int:idproyecto>/<int:version>/', obtener_planificacion_version, name='planificacion_version'),
    path(r'planificaciones/contar/', contar_planificaciones, name='contar_planificaciones'),
    path(r'planificacion/actividades-plan/<int:idproyecto>/', procesar_actividades_planificacion_bulk, name='bulk-actividades-planificacion'),
    #Actividades-Tareas
    path(r'actividades-con-tareas/', ActividadConTareasListView.as_view(), 
         name='actividades-con-tareas'),
    path(r'tarea-detalles/<int:tarea_id>/', obtener_tarea_detalle, name='obtener_tarea_detalle'),     
    path(r'actividades-con-tareas/<int:pk>/', ActividadConTareasDetailView.as_view(), name='actividad-detalle-con-tareas'),
    #Ruta de actividad
    path(r'actividades/<int:actividad_id>/ruta-proyecto/', ruta_actividad_proyecto, name="ruta_actividad_proyecto"),
    #Rutas de actividad
    path(r'actividades/<int:actividad_id>/rutas/', rutas_actividad, name="rutas_actividad"),
    path(r'actividad/<int:actividad_id>/ruta-con-indicadores/', obtener_ruta_actividad_con_indicadores, name='obtener_ruta_actividad_indicadores'),
    path(r'actividad/<int:actividad_id>/all-rutas-con-indicadores/', rutas_actividad_indicadores, name='obtener_rutas_actividad_indicadores'),
    #Lista de actividades por responsable
    #Objetivos e indicadores para PEI
    path(r'pei/<int:pei_id>/objetivos-pei/',ObjetivoPeiPorPeiListView.as_view(), name='objetivospei_por_pei'),
    path(r'pei/<int:pei_id>/indicadores-pei/', IndicadorPeiPorPeiListView.as_view(), name='indicadorespeo_por_pei'),
    #Monitoreo
    path(r'monitoreo/crear-solicitud-fondos/', crear_solicitud_fondos, name='crear_solicitud_fondos'),
    path(r'monitoreo/solicitud-viaje/<int:pk>/', solicitud_viaje_detail, name='sol-viaje-detalle'),
    path(r'monitoreo/lista-solicitud-viaje/', solicitud_viaje_list, name='lista-sol-viaje'),
    path(r'monitoreo/crear-solicitud-viaje/', crear_solicitud_viaje, name='crear-sol-viaje'),
    path(r'monitoreo/obtener-datos-formulario/', obtener_datos_solicitud_fondos, name='obt_datos_form_sol_fondos'),
    path(r'monitoreo/crear-rendicion-cuentas/', crear_rendicion_cuentas, name='form_rendicion_cuentas'),
    path(r'monitoreo/rendicion-cuentas-datos/', RendicionCuentasDatosView.as_view(), name='rendicion-cuentas-datos-form'),
    #Diagrama de Gannt
    path(r'actividades-gannt/', actividades_con_estados, name='actividades-diagrama-gannt' ),
    #INFORMDE DE TAREA - SUBACTIVIDAD
    #Guardar
    path(r'informes-tarea/crear/', crear_informe_tarea, name='crear-informe-tarea'),
    #Extraer/Obtener
    path(r'informes-tarea/listar/', listar_informes_tarea, name='listar-informes-tareas'),
    path(r'informes-tarea/obtener/<int:informe_id>/', obtener_informe_tarea, name='obtener-informe-tarea'),
    #Actualizar
    path(r'informes-tarea/actualizar/<int:informe_id>/', actualizar_informe_tarea, name='actualizar-informe-tarea'),
    #Eliminar
    path(r'informes-tarea/eliminar/<int:informe_id>/', eliminar_informe_tarea, name='eliminar-informe-tarea'),
]

urlpatterns += router.urls