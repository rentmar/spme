from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerUsuario/',views.ObtenerUsuario.as_view(), name='obtenerUsuario'),
    path(r'crearUsuario/',views.CrearUsuario.as_view(), name='crearUsuario'),
    path(r'autenticarUsuario/',views.AutenticacionUsuario.as_view(), name='autenticarUsuario'),
    path(r'listaUsuarios/',views.ListaUsuarios.as_view(), name='listaUsuarios'),
    path(r'listaValidadores/',views.ListaValidadores.as_view(), name='listaValidadores'),
    path(r'api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(r'api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(r'api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
urlpatterns += router.urls