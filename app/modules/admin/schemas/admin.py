from datetime import datetime

from pydantic import BaseModel

from app.db.models.hoja_vida import TipoItemHojaVida
from app.db.models.postulacion import PostulacionEstado


# -- Phase 13: Admin item detalle with nested soportes --

class AdminSoporteItemSimple(BaseModel):
    id_soporte: int
    nombre_archivo: str
    url_archivo: str
    tipo_archivo: str
    tamanio_bytes: int
    fecha_carga: datetime


class AdminItemDetalle(BaseModel):
    id_item: int
    tipo_item: TipoItemHojaVida
    descripcion: str
    institucion: str | None = None
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    cantidad: int | None = None
    puntaje_asignado: float | None = None
    validado: bool = False
    soportes: list[AdminSoporteItemSimple] = []


class AdminPostulacionDetalleCompleto(BaseModel):
    """Contract 13.16: full admin review with items and nested soportes."""
    id_postulacion: int
    id_usuario: int
    aspirante_nombre: str
    aspirante_apellido: str
    aspirante_cedula: str
    aspirante_email: str
    id_convocatoria: int
    titulo_convocatoria: str
    estado: PostulacionEstado
    puntaje_total: float | None
    fecha_envio: datetime | None = None
    fecha_evaluacion: datetime | None = None
    observaciones_admin: str | None = None
    items: list[AdminItemDetalle]


# -- Phase 13: Item validation --

class ItemValidationResponse(BaseModel):
    id_item: int
    validado: bool
    tipo_item: TipoItemHojaVida
    descripcion: str


# -- Phase 13: Admin observaciones --

class ObservacionesPayload(BaseModel):
    observaciones_admin: str | None = None


class ObservacionesResponse(BaseModel):
    id_postulacion: int
    observaciones_admin: str | None = None


# -- Phase 13: Evaluation trace --
# Updated for Fase 14: includes regla_aplicada, sin_regla, id_convocatoria, advertencias

class ReglaAplicadaInfo(BaseModel):
    id_regla: int
    descripcion_regla: str


class EvaluationTraceItem(BaseModel):
    id_item: int
    tipo_item: TipoItemHojaVida
    descripcion: str
    cantidad: int
    puntaje_unitario: float
    maximo_acumulable: float | None
    puntaje_asignado: float
    regla_aplicada: ReglaAplicadaInfo | None = None
    sin_regla: bool = False


class EvaluationTraceResponse(BaseModel):
    """Contract 13.17 / 14.17: how the total score was built."""
    id_postulacion: int
    id_convocatoria: int
    puntaje_total: float
    detalle_evaluacion: list[EvaluationTraceItem]
    advertencias: list[str] = []


class AdminAspirantSummary(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    cedula: str
    email: str
    telefono: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    fecha_registro: datetime


class AdminAspirantDetail(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    cedula: str
    email: str
    telefono: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    pais: str | None = None
    postulaciones: list[dict]


class AdminSoporteItem(BaseModel):
    id_soporte: int
    id_item: int
    nombre_archivo: str
    url_archivo: str
    tipo_archivo: str
    tamanio_bytes: int
    fecha_carga: datetime


class AdminPostulacionDetalle(BaseModel):
    id_postulacion: int
    id_usuario: int
    aspirante_nombre: str
    aspirante_apellido: str
    aspirante_cedula: str
    titulo_convocatoria: str
    estado: PostulacionEstado
    puntaje_total: float | None
    url_cv_original: str | None = None
    observaciones_admin: str | None = None
    fecha_envio: datetime | None = None
    fecha_evaluacion: datetime | None = None
    total_items: int
    soportes: list[AdminSoporteItem]
