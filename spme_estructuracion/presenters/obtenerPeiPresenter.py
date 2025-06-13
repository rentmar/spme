from ..domain.models.response.listPeiResponse import ListaPeiResponse,PeiResponse
from ..mappers.listPeiMapper import ListPeiMapper
from ..domain.usecases.obtenerListaPeiUseCase import ObtenerListaPeiUseCase

class ObtenerPeiPresenter:

    def listaPei(self):
        """
        Método para obtener la lista de PEI en el formato esperado.
        
        :param peiData: Datos del PEI a ser formateados.
        :return: Lista de PEI serializada.
        """
        #------------------------------------------
        # peiResponse = {
        #     "id": 1,
        #     "titulo": "PEI Ejemplo",
        #     "descripcion": "Descripción del PEI de ejemplo",
        #     "fecha_creacion": "2023-01-01",
        #     "fecha_inicio": "2023-01-01",
        #     "fecha_fin": "2025-01-01",
        #     "esta_vigente": True,
        #     "creado_el": "2023-01-01T00:00:00Z",
        #     "modificado_el": "2023-01-02T00:00:00Z"
        # }
        # peiSerializer  = PeiResponse(data=peiResponse)
        # peiSerializer.is_valid(raise_exception=True)
        #------------------------------------------
        #listaPei = [peiSerializer.data] #objeto de tipo list
        listaPeiUseCase = ObtenerListaPeiUseCase()
        qsPei = listaPeiUseCase.execute()  # Obtiene la lista de PEI desde el caso de uso
        return ListPeiMapper.toListPeiResponse(qsPei) #pone los datos en el formato esperado