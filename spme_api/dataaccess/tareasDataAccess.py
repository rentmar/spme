from spme_web.models import Tarea


class TareasDataAccess:
    def getTareas(self):
        queryset = Tarea.objects.all() #Uso de ORM
        return queryset



