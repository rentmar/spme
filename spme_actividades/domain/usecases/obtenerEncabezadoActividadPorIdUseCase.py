from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer
from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
from spme_actividades.container.repositoryContainer import ActividadTipoRepositoryContainer

class ObtenerEncabezadoActividadPorIdUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()
        self.userRepository = UserRepositoryContainer().userRepository()
        self.actividadTipoRepository = ActividadTipoRepositoryContainer().actividadTipoRepository()

    def execute(self, encabezadoRequest):
        datosEncabezado = self.actividadesRepository.obtenerEncabezadoActividadPorId(encabezadoRequest['id'])

        if datosEncabezado is None:
            return None

        datosUsuario = self.userRepository.obtenerNombreUsuarioPorId(datosEncabezado['responsable_id'])

        if datosUsuario is not None:
            datosEncabezado['nombre_responsable'] = datosUsuario['nombre'] + " " + datosUsuario['paterno'] + " " + datosUsuario['materno']

        tipoActividad = self.actividadTipoRepository.obtenerTipoActividadPorId(datosEncabezado['tipo_id'])

        if tipoActividad is not None:
            datosEncabezado['tipo_actividad'] = tipoActividad.tipo_actividad

        return datosEncabezado