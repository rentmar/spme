from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerUsuario/',views.GetUserByName.as_view(), name='obtenerUsuario'),
    path(r'crearUsuario/',views.CreateUser.as_view(), name='crearUsuario'),
]
urlpatterns += router.urls