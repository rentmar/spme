from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerActividadesUsuario/',views.ObtenerActividadesUsuario.as_view(), name='obtenerActividadesUsuario'),
]
urlpatterns += router.urls