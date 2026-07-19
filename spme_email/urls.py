from django.urls import path, include
from rest_framework.routers import DefaultRouter

#Import para dev
from .views.email_test_views import PreviewEmailView

from .views.email_views import (
    TestSimpleEmailView, 
    SendTemplatedEmailView,
    SendAsyncEmailView,
)

#Envio de notificaciones email para formularios
from .views.notificacion_views import NotificacionSolicitudView

router = DefaultRouter()

urlpatterns = [
    # path(r'actualizar-validacion-solicitud-pago-directo/', views.ActualizarValidacionSolicitudPagoDirecto.as_view(), name='actualizar_validacion_solicitud_pago_directo'),
    #Previsualizacion de templates
    path(r'email/preview/', PreviewEmailView.as_view(), name='email_preview_list'),
    path(r'email/preview/<str:template_name>/', PreviewEmailView.as_view(), name='email_preview'),
    #Envio de email simple
    path(r'email/test-simple/', TestSimpleEmailView.as_view(), name="test-simple-email"),
    #Envio de emails usando templates
    path(r'email/template/send/', SendTemplatedEmailView.as_view(), name="send-email"),
    #Envio asincrono de email
    path(r'email/template/send-async/', SendAsyncEmailView.as_view(), name="send-async-email"),
    #Envio de notificaciones para formularios
    path(r'email/notificaciones/enviar/', NotificacionSolicitudView.as_view(), name='enviar_notificacion'),
]
urlpatterns += router.urls