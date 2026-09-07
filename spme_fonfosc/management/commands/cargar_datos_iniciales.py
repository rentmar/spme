from django.core.management.base import BaseCommand
from django.db import transaction

from spme_fonfosc.models import (
    DepartamentoBolivia,
    Institucion,
)


class Command(BaseCommand):
    help = "Carga los datos iniciales de FONFOSC: departamentos e instituciones."

    # ============================================================
    # DEPARTAMENTOS DE BOLIVIA
    # ============================================================

    DEPARTAMENTOS = [
        ("BEN", "Beni"),
        ("CHU", "Chuquisaca"),
        ("CBA", "Cochabamba"),
        ("LP", "La Paz"),
        ("OR", "Oruro"),
        ("PAN", "Pando"),
        ("PT", "Potosí"),
        ("SCZ", "Santa Cruz"),
        ("TAR", "Tarija"),
    ]

    # ============================================================
    # INSTITUCIONES RED UNITAS
    # ============================================================

    INSTITUCIONES = [
        {
            "sigla": "ACLO",
            "nombre": "Fundación Acción Cultural Loyola",
            "emailInstitucion": "aclogeneral@aclo.org.bo",
            "telefono": None,
            "direccion": None,
            "ciudad": "Sucre",
            "departamentoSede": "CHU",
            "casillaPostal": None,
            "webSite": "https://www.aclo.org.bo/",
            "departamentosIntervencion": ["CHU", "PT", "TAR"],
        },
        {
            "sigla": "CASA DE LA MUJER",
            "nombre": "Casa de la Mujer",
            "emailInstitucion": None,
            "telefono": None,
            "direccion": None,
            "ciudad": "Santa Cruz de la Sierra",
            "departamentoSede": "SCZ",
            "casillaPostal": None,
            "webSite": "https://casadelamujer.org.bo/",
            "departamentosIntervencion": ["SCZ"],
        },
        {
            "sigla": "CEDLA",
            "nombre": "Centro de Estudios para el Desarrollo Laboral y Agrario",
            "emailInstitucion": "info@cedla.org",
            "telefono": None,
            "direccion": None,
            "ciudad": "La Paz",
            "departamentoSede": "LP",
            "casillaPostal": None,
            "webSite": "https://cedla.org/",
            "departamentosIntervencion": [],
        },
        {
            "sigla": "CEJIS",
            "nombre": "Centro de Estudios Jurídicos e Investigación Social",
            "emailInstitucion": "cejis@cejis.org",
            "telefono": None,
            "direccion": None,
            "ciudad": "Santa Cruz de la Sierra",
            "departamentoSede": "SCZ",
            "casillaPostal": None,
            "webSite": "https://www.cejis.org/",
            "departamentosIntervencion": [],
        },
        {
            "sigla": "CENDA",
            "nombre": "Centro de Comunicación y Desarrollo Andino",
            "emailInstitucion": "info@cenda.org",
            "telefono": None,
            "direccion": None,
            "ciudad": "Cochabamba",
            "departamentoSede": "CBA",
            "casillaPostal": None,
            "webSite": "https://www.cenda.org/",
            "departamentosIntervencion": ["CBA"],
        },
        {
            "sigla": "CERDET",
            "nombre": "Centro de Estudios Regionales para el Desarrollo de Tarija",
            "emailInstitucion": "cerdet@cerdet.org.bo",
            "telefono": None,
            "direccion": None,
            "ciudad": "Tarija",
            "departamentoSede": "TAR",
            "casillaPostal": None,
            "webSite": "https://www.cerdet.org.bo/",
            "departamentosIntervencion": ["TAR"],
        },
        {
            "sigla": "CIAC",
            "nombre": "Centro de Investigación y Apoyo Campesino",
            "emailInstitucion": None,
            "telefono": None,
            "direccion": None,
            "ciudad": None,
            "departamentoSede": None,
            "casillaPostal": None,
            "webSite": "https://ciac-idr.com/",
            "departamentosIntervencion": [],
        },
        {
            "sigla": "CIPCA",
            "nombre": "Centro de Investigación y Promoción del Campesinado",
            "emailInstitucion": "cipca@cipca.org.bo",
            "telefono": None,
            "direccion": None,
            "ciudad": "La Paz",
            "departamentoSede": "LP",
            "casillaPostal": None,
            "webSite": "https://cipca.org.bo/",
            "departamentosIntervencion": ["LP", "CBA", "SCZ", "BEN"],
        },
        {
            "sigla": "CIUDADANÍA",
            "nombre": "Ciudadanía, Comunidad de Estudios Sociales y Acción Pública",
            "emailInstitucion": "ciudadania@ciudadaniabolivia.org",
            "telefono": None,
            "direccion": None,
            "ciudad": "Cochabamba",
            "departamentoSede": "CBA",
            "casillaPostal": None,
            "webSite": "https://www.ciudadaniabolivia.org/",
            "departamentosIntervencion": ["CBA"],
        },
        {
            "sigla": "DNI-BOLIVIA",
            "nombre": "Defensa de Niñas y Niños Internacional - Sección Bolivia",
            "emailInstitucion": "presidencia@dni-bolivia.org.bo",
            "telefono": None,
            "direccion": "Av. Japón Nº 3355, Piso 3, Zona Senkata",
            "ciudad": "El Alto",
            "departamentoSede": "LP",
            "casillaPostal": None,
            "webSite": "https://dni-bolivia.org.bo/",
            "departamentosIntervencion": ["LP", "CBA", "OR"],
        },
        {
            "sigla": "SARTAWI SAYARIY",
            "nombre": "Fundación Sartawi Sayariy",
            "emailInstitucion": "sartawi@sayariy.org",
            "telefono": None,
            "direccion": None,
            "ciudad": "La Paz",
            "departamentoSede": "LP",
            "casillaPostal": None,
            "webSite": "https://www.fundacionsartawi.org/",
            "departamentosIntervencion": ["LP", "OR", "PT"],
        },
        {
            "sigla": "URAMANTA",
            "nombre": "Fundación Uramanta",
            "emailInstitucion": "fsuramanta@uramanta.org",
            "telefono": None,
            "direccion": None,
            "ciudad": "Cochabamba",
            "departamentoSede": "CBA",
            "casillaPostal": None,
            "webSite": None,
            "departamentosIntervencion": ["CBA"],
        },
        {
            "sigla": "IICCA",
            "nombre": "Instituto de Investigación y Capacitación Campesina",
            "emailInstitucion": "info@iiccatarija.com",
            "telefono": None,
            "direccion": None,
            "ciudad": "Tarija",
            "departamentoSede": "TAR",
            "casillaPostal": None,
            "webSite": "https://iiccatarija.com/",
            "departamentosIntervencion": ["TAR"],
        },
        {
            "sigla": "INDICEP",
            "nombre": "Instituto de Investigación Cultural para la Educación Popular",
            "emailInstitucion": "admin@indicep.org",
            "telefono": None,
            "direccion": None,
            "ciudad": "Cochabamba",
            "departamentoSede": "CBA",
            "casillaPostal": None,
            "webSite": "https://indicep.org/",
            "departamentosIntervencion": ["CBA"],
        },
        {
            "sigla": "IPTK",
            "nombre": "Instituto Politécnico Tomás Katari",
            "emailInstitucion": "iptk@iptk.org.bo",
            "telefono": None,
            "direccion": None,
            "ciudad": "Sucre",
            "departamentoSede": "CHU",
            "casillaPostal": None,
            "webSite": "https://iptk.org.bo/",
            "departamentosIntervencion": ["CHU", "PT"],
        },
        {
            "sigla": "ISALP",
            "nombre": "Investigación Social y Asesoramiento Legal Potosí",
            "emailInstitucion": "isalp@entelnet.bo",
            "telefono": "(591) 2 6224192 / 2 6226228",
            "direccion": "Calle Sucre Nº 69",
            "ciudad": "Potosí",
            "departamentoSede": "PT",
            "casillaPostal": "326",
            "webSite": "https://isalp.org.bo/",
            "departamentosIntervencion": ["PT"],
        },
        {
            "sigla": "KURMI-ADSI",
            "nombre": "KURMI - Apoyo al Desarrollo Sostenible Interandino",
            "emailInstitucion": "kurmi.adsi@gmail.com",
            "telefono": None,
            "direccion": None,
            "ciudad": "Tiquipaya",
            "departamentoSede": "CBA",
            "casillaPostal": None,
            "webSite": "https://www.kurmi-adsi.org/",
            "departamentosIntervencion": ["CBA"],
        },
        {
            "sigla": "LIDER",
            "nombre": "Línea Institucional de Desarrollo Rural",
            "emailInstitucion": "lidersucre@gmail.com",
            "telefono": "64-26004 / 64-34903",
            "direccion": "Calle Tupac Yupanqui Nº 365",
            "ciudad": "Sucre",
            "departamentoSede": "CHU",
            "casillaPostal": None,
            "webSite": "https://lider.org.bo/",
            "departamentosIntervencion": ["CHU"],
        },
        {
            "sigla": "MUJERES EN ACCIÓN",
            "nombre": "Mujeres en Acción",
            "emailInstitucion": "mujeresenaccion25@gmail.com",
            "telefono": "591-46667093",
            "direccion": "Calle Raúl Pacheco S/N, Zona Aeropuerto",
            "ciudad": "Tarija",
            "departamentoSede": "TAR",
            "casillaPostal": None,
            "webSite": "https://mujeresenaccion.org.bo/",
            "departamentosIntervencion": ["TAR"],
        },
        {
            "sigla": "APROSAR",
            "nombre": "Asociación de Promotores de Salud Rural",
            "emailInstitucion": "contacto@aprosarbolivia.org.bo",
            "telefono": None,
            "direccion": None,
            "ciudad": "Oruro",
            "departamentoSede": "OR",
            "casillaPostal": None,
            "webSite": "https://aprosarbolivia.org.bo/",
            "departamentosIntervencion": ["OR"],
        },
        {
            "sigla": "PASCAR",
            "nombre": "Pastoral Social Cáritas Sucre",
            "emailInstitucion": "pascarsr@gmail.com",
            "telefono": None,
            "direccion": None,
            "ciudad": "Sucre",
            "departamentoSede": "CHU",
            "casillaPostal": None,
            "webSite": "https://caritasbolivia.org/",
            "departamentosIntervencion": ["CHU"],
        },
        {
            "sigla": "PROCESO",
            "nombre": "PROCESO Servicios Educativos",
            "emailInstitucion": "proceso-edu@scbbs-bo.com",
            "telefono": None,
            "direccion": None,
            "ciudad": "Santa Cruz de la Sierra",
            "departamentoSede": "SCZ",
            "casillaPostal": None,
            "webSite": None,
            "departamentosIntervencion": ["SCZ"],
        },
        {
            "sigla": "RADIO PÍO XII",
            "nombre": "Radio Pío XII",
            "emailInstitucion": None,
            "telefono": None,
            "direccion": None,
            "ciudad": "Cochabamba",
            "departamentoSede": "CBA",
            "casillaPostal": None,
            "webSite": "https://radiopio12.com.bo/",
            "departamentosIntervencion": ["PT", "OR", "CBA"],
        },
        {
            "sigla": "SEMTA",
            "nombre": "Servicios Múltiples de Tecnologías Apropiadas",
            "emailInstitucion": None,
            "telefono": None,
            "direccion": None,
            "ciudad": None,
            "departamentoSede": None,
            "casillaPostal": None,
            "webSite": None,
            "departamentosIntervencion": [],
        },
    ]

    # ============================================================
    # EJECUCIÓN
    # ============================================================

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Carga de datos iniciales de FONFOSC"
            )
        )
        self.stdout.write("")

        # --------------------------------------------------------
        # 1. DEPARTAMENTOS
        # --------------------------------------------------------

        self.stdout.write(
            self.style.HTTP_INFO(
                "1. Cargando departamentos de Bolivia..."
            )
        )

        departamentos = {}

        for codigo, nombre in self.DEPARTAMENTOS:

            departamento, creado = DepartamentoBolivia.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                },
            )

            departamentos[codigo] = departamento

            if creado:
                self.stdout.write(
                    f"  + Departamento creado: {codigo} - {nombre}"
                )
            else:
                self.stdout.write(
                    f"  = Departamento existente: {codigo} - {nombre}"
                )

        self.stdout.write("")

        # --------------------------------------------------------
        # 2. INSTITUCIONES
        # --------------------------------------------------------

        self.stdout.write(
            self.style.HTTP_INFO(
                "2. Cargando instituciones de la Red UNITAS..."
            )
        )

        creadas = 0
        actualizadas = 0

        for datos in self.INSTITUCIONES:

            # Copiamos el diccionario para no modificar
            # la definición original.
            datos_institucion = datos.copy()

            departamentos_intervencion = datos_institucion.pop(
                "departamentosIntervencion",
                []
            )

            codigo_sede = datos_institucion.pop(
                "departamentoSede",
                None
            )

            # ----------------------------------------------------
            # Resolver departamento de sede
            # ----------------------------------------------------

            departamento_sede = None

            if codigo_sede:
                departamento_sede = departamentos.get(codigo_sede)

                if departamento_sede is None:
                    raise ValueError(
                        f"El departamento de sede '{codigo_sede}' "
                        f"no existe."
                    )

            datos_institucion["departamentoSede"] = departamento_sede

            # ----------------------------------------------------
            # Buscar institución existente
            # ----------------------------------------------------

            sigla = datos_institucion.get("sigla")
            nombre = datos_institucion.get("nombre")

            institucion = None

            if sigla:
                institucion = (
                    Institucion.objects
                    .filter(sigla__iexact=sigla)
                    .first()
                )

            if institucion is None and nombre:
                institucion = (
                    Institucion.objects
                    .filter(nombre__iexact=nombre)
                    .first()
                )

            # ----------------------------------------------------
            # Crear o actualizar
            # ----------------------------------------------------

            if institucion:

                for campo, valor in datos_institucion.items():
                    setattr(institucion, campo, valor)

                institucion.save()

                actualizadas += 1

                self.stdout.write(
                    f"  = Actualizada: {sigla}"
                )

            else:

                institucion = Institucion.objects.create(
                    **datos_institucion
                )

                creadas += 1

                self.stdout.write(
                    f"  + Creada: {sigla}"
                )

            # ----------------------------------------------------
            # Departamentos de intervención
            # ----------------------------------------------------

            instituciones_intervencion = []

            for codigo_departamento in departamentos_intervencion:

                departamento = departamentos.get(
                    codigo_departamento
                )

                if departamento is None:
                    raise ValueError(
                        f"El departamento de intervención "
                        f"'{codigo_departamento}' no existe."
                    )

                instituciones_intervencion.append(
                    departamento
                )

            institucion.departamentoIntervencion.set(
                instituciones_intervencion
            )

        # --------------------------------------------------------
        # RESUMEN
        # --------------------------------------------------------

        total_departamentos = DepartamentoBolivia.objects.count()
        total_instituciones = Institucion.objects.count()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Carga de datos iniciales completada"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )

        self.stdout.write(
            f"Departamentos registrados : {total_departamentos}"
        )

        self.stdout.write(
            f"Instituciones registradas : {total_instituciones}"
        )

        self.stdout.write(
            f"Instituciones creadas     : {creadas}"
        )

        self.stdout.write(
            f"Instituciones actualizadas: {actualizadas}"
        )

        self.stdout.write("")