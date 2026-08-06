"""
URL configuration for spme project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('autenticacion_api/', include('spme_autenticacion.urls')),
    path('admin/', admin.site.urls),
    path('', include('spme_web.urls')),
    path('estructuracionPei_api/', include('spme_estructuracion_pei.urls')),
    path('actividades_api/', include('spme_actividades.urls')),
    path('monitoreo_api/', include('spme_monitoreo.urls')),
    #Api de planificacion
    path('api-plan/', include('spme_planificacion.urls')),
    #Api de transicion
    path('api/', include('apptran.urls')),
    #Api de configuracion
    path('api/system/', include('system_config.urls') ),
    #Api Programas/Areas
    path('api-ap/', include('spme_programas.urls')),
    #Api de proyectos
    path('api-proy/', include('spme_estructuracion_proyecto.urls'),),
    #Api de reportes
    path('api-rep/', include('spme_proyectos_reportes.urls')),
    #Api de gestion acceso
    path('api-gaxs/', include('spme_gestion_acceso.urls')),
    #Api de mensajeria
    path('api-msg/', include('spme_mensajes.urls')),
    #Api de fonfosc
    path('api-ff/', include('spme_fonfosc.urls')),
    #Api para impresiones
    path('api-print/', include('spme_impresiones.urls')),
    #Api para valida
    path('api-valid/', include('spme_validaciones.urls')),
    #Api Reportes pei
    path('api-peirep/', include('spme_pei_reportes.urls')),
    #Api presupuestos
    path('api-pres/', include('spme_presupuesto.urls')),
    #Api emails
    path('api-mail/', include('spme_email.urls')),
    #Api repositorio
    path('api-repo/', include('spme_repositorio.urls')),
    #Api reporte tree
    path('api-rtree/', include('spme_tree_reporter.urls'))
] 

