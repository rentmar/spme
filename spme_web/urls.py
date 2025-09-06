from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
#router.register(r'tareas-endpoint', TareaView, basename='proyecto-plan')

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += router.urls
