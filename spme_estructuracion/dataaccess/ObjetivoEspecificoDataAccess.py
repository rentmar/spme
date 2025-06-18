from ..models import ObjetivoEspecificoProyecto

class ObjetivoEspecificoDataAccess:
    #Instancia Producto
    def objetivoEspecificoTodo(self):
        objetivoEspecifico = ObjetivoEspecificoProyecto.objects.all()
        return objetivoEspecifico
    
    def objetivoEspecificoPorId(self, id):
        objetivoEspecifico = ObjetivoEspecificoProyecto.objects.filter(id=id).first()
        return objetivoEspecifico
