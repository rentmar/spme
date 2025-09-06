from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.programa_views import (
    ProgramaViewset
    )


router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
router.register(r'programas', ProgramaViewset, basename='programas-areas')

urlpatterns = [
    #path(r'programa/test/', test_endpoint, name='test_endpoint'), 

]

urlpatterns += router.urls

