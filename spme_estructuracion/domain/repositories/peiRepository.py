from ...dataaccess.peiDataAccess import PeiDataAccess

class PeiRepository:
    def getListaPei(self):
        peiDataAccess = PeiDataAccess()
        qsPei = peiDataAccess.getListaPei()
        return qsPei
