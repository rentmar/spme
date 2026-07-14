from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.email_views import (
    TestSimpleEmailView, 
    PreviewEmailView, 
    SendTemplatedEmailView,
    SendAsyncEmailView,
)

router = DefaultRouter()

urlpatterns = [
    # path(r'actualizar-validacion-solicitud-pago-directo/', views.ActualizarValidacionSolicitudPagoDirecto.as_view(), name='actualizar_validacion_solicitud_pago_directo'),
    #Envio de email simple
    path(r'email/test-simple/', TestSimpleEmailView.as_view(), name="test-simple-email"),
    #Previsualizacion de templates
    path(r'email/preview/<str:template_name>/', PreviewEmailView.as_view(), name="preview-email"),
    #Envio de emails usando templates
    path(r'email/template/send/', SendTemplatedEmailView.as_view(), name="send-email"),
    #Envio asincrono de email
    path(r'email/template/send-async/', SendAsyncEmailView.as_view(), name="send-async-email"),
]
urlpatterns += router.urls