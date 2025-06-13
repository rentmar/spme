from ..models import Pei

class PeiDataAccess:

    def getListaPei(self):
        return Pei.objects.all()
    