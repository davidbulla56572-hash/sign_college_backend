from datetime import datetime

from pydantic import BaseModel

from app.db.models.postulacion import PostulacionEstado


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
