# Endpoints de Rendición de Cuentas PEI

## Base URL
`http://127.0.0.1:8000/api/rendicion-cuentas-pei/`

---

## 1. Crear Rendición de Cuentas
**Endpoint:** `POST /api/rendicion-cuentas-pei/`

**Descripción:** Crea una nueva rendición de cuentas con generación automática de ID y numeroFormulario.

**Request Body (todos los datos de la tabla):**
```json
{
  "cpteDiario": "CPT-2024-001",
  "fechaDesembolso": "2024-01-15",
  "montoAsignado": 5000.00,
  "montoDescargado": 3500.00,
  "saldo": 1500.00,
  "detalleDestinoFondos": [],
  "actividad_id": 5,
  "fechaActividad": "2024-01-20",
  "descripcionActividad": "Descripción de la actividad",
  "lugarActividad": "Lugar de la actividad",
  "lugarRendicion": "Lugar de rendición",
  "tarea_id": 9,
  "usuario_id": 7,
  "solicitudFondos_id": null,
  "solicitudReembolso_id": null,
  "solicitudViaje_id": null,
  "solicitudPagoDirecto_id": null
}
```

**Response:**
```json
{
  "id": 45,
  "numeroFormulario": "ACT - RCPEI 0045",
  "cpteDiario": "CPT-2024-001",
  "fechaDesembolso": "2024-01-15",
  "montoAsignado": 5000.00,
  "montoDescargado": 3500.00,
  "saldo": 1500.00,
  "detalleDestinoFondos": [],
  "actividad_id": 5,
  "fechaActividad": "2024-01-20",
  "fechaRendicion": "2024-01-20",
  "descripcionActividad": "Descripción de la actividad",
  "lugarActividad": "Lugar de la actividad",
  "lugarRendicion": "Lugar de rendición",
  "tarea_id": 9,
  "bloquearIconos": true,
  "validacionResponsable": false,
  "validacionCoordinador": false,
  "validacionContador": false,
  "validacionAdministrador": false,
  "usuario_id": 7,
  "solicitudFondos_id": null,
  "solicitudReembolso_id": null,
  "solicitudViaje_id": null,
  "solicitudPagoDirecto_id": null
}
```

**Notas:**
- `id` se genera automáticamente
- `numeroFormulario` se genera automáticamente con formato: `{codigo_actividad} - RCPEI {id_formateado}`
- `fechaRendicion` se genera automáticamente con la fecha actual
- Los campos de validación (`validacionResponsable`, `validacionCoordinador`, etc.) por defecto son `false`

---

## 2. Obtener Todas las Rendiciones de Cuentas
**Endpoint:** `GET /api/rendicion-cuentas-pei/`

**Descripción:** Obtiene todos los registros de rendición de cuentas.

**Request:** No requiere request body.

**Response:**
```json
[
  {
    "id": 1,
    "numeroFormulario": "ACT - RCPEI 0001",
    "cpteDiario": "CPT-2024-001",
    "fechaDesembolso": "2024-01-15",
    "montoAsignado": 5000.00,
    "montoDescargado": 3500.00,
    "saldo": 1500.00,
    "detalleDestinoFondos": [],
    "actividad_id": 5,
    "fechaActividad": "2024-01-20",
    "fechaRendicion": "2024-01-20",
    "descripcionActividad": "Descripción de la actividad",
    "lugarActividad": "Lugar de la actividad",
    "lugarRendicion": "Lugar de rendición",
    "tarea_id": 9,
    "bloquearIconos": true,
    "validacionResponsable": false,
    "validacionCoordinador": false,
    "validacionContador": false,
    "validacionAdministrador": false,
    "usuario_id": 7,
    "solicitudFondos_id": null,
    "solicitudReembolso_id": null,
    "solicitudViaje_id": null,
    "solicitudPagoDirecto_id": null
  },
  {
    "id": 2,
    "numeroFormulario": "ACT - RCPEI 0002",
    ...
  }
]
```

---

## 3. Filtrar Rendiciones de Cuentas
**Endpoint:** `POST /api/rendicion-cuentas-pei/filtrar/`

**Descripción:** Obtiene rendiciones de cuentas filtrando por actividad_id, usuario_id y tarea_id.

**Request Body:**
```json
{
  "actividad_id": 5,
  "usuario_id": 7,
  "tarea_id": 9
}
```

**Notas:**
- `actividad_id` y `usuario_id` son requeridos
- `tarea_id` es opcional y puede ser `null`
- Todos los filtros se aplican si están presentes

**Response:**
```json
[
  {
    "id": 3,
    "numeroFormulario": "ACT - RCPEI 0003",
    "actividad_id": 5,
    "usuario_id": 7,
    "tarea_id": 9,
    ...
  }
]
```

---

## 4. Actualizar Estado de Validación
**Endpoint:** `PATCH /api/rendicion-cuentas-pei/actualizar_estado/`

**Descripción:** Actualiza el estado de validación (validacionResponsable o validacionCoordinador) de una rendición de cuentas.

**Request Body:**
```json
{
  "id": 3,
  "validacionResponsable": true
}
```

O alternativamente:
```json
{
  "id": 3,
  "validacionCoordinador": true
}
```

**Notas:**
- `id` es requerido
- Solo uno de los campos de validación es necesario, pero ambos pueden actualizarse
- El endpoint acepta cualquier combinación de los campos de validación

**Response:**
```json
{
  "id": 3,
  "numeroFormulario": "ACT - RCPEI 0003",
  "validacionResponsable": true,
  "validacionCoordinador": false,
  ...
}
```

---

## Campos de la Tabla RendicionCuentasActPei

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID autogenerado |
| numeroFormulario | String(150) | Número de formulario autogenerado |
| cpteDiario | String(100) | Comprobante diario |
| fechaDesembolso | Date | Fecha de desembolso |
| montoAsignado | Decimal | Monto asignado |
| montoDescargado | Decimal | Monto descargado (requerido) |
| saldo | Decimal | Saldo |
| detalleDestinoFondos | JSONField | Detalle del destino de fondos |
| actividad_id | Integer | FK a ActividadPei |
| fechaActividad | Date | Fecha de la actividad |
| fechaRendicion | Date | Fecha de rendición (autogenerado) |
| descripcionActividad | Text | Descripción de la actividad |
| lugarActividad | Text | Lugar de la actividad |
| lugarRendicion | Text | Lugar de rendición |
| tarea_id | Integer | FK a TareaActividadPei (opcional) |
| bloquearIconos | Boolean | Bloquear iconos (default: true) |
| validacionResponsable | Boolean | Validación del responsable (default: false) |
| validacionCoordinador | Boolean | Validación del coordinador (default: false) |
| validacionContador | Boolean | Validación del contador (default: false) |
| validacionAdministrador | Boolean | Validación del administrador (default: false) |
| responsable_id | Integer | FK a Usuario (responsable) |
| coordinador_id | Integer | FK a Usuario (coordinador) |
| contador_id | Integer | FK a Usuario (contador) |
| administrador_id | Integer | FK a Usuario (administrador) |
| usuario_id | Integer | FK a Usuario |
| solicitudFondos_id | Integer | FK a SolicitudFondosActPei |
| solicitudReembolso_id | Integer | FK a SolicitudReembolsoActPei |
| solicitudViaje_id | Integer | FK a SolicitudViajeActPei |
| solicitudPagoDirecto_id | Integer | FK a SolicitudPagoDirectoActPei |
