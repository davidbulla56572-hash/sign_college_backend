from datetime import datetime

from pydantic import BaseModel

from app.db.models.postulacion import PostulacionEstado


class PostulacionCreate(BaseModel):
    id_convocatoria: int


class ActiveDraftResponse(BaseModel):
    """Response for create/recover draft for active convocatoria."""
    id_postulacion: int
    id_convocatoria: int
    estado: PostulacionEstado
    ya_existia: bool


class PostulacionSummary(BaseModel):
    id_postulacion: int
    id_convocatoria: int
    titulo_convocatoria: str | None = None
    estado: PostulacionEstado
    puntaje_total: float | None = None
    fecha_envio: datetime | None = None


class PostulacionDetail(BaseModel):
    id_postulacion: int
    id_usuario: int
    id_convocatoria: int
    titulo_convocatoria: str | None = None
    estado: PostulacionEstado
    puntaje_total: float | None = None
    url_cv_original: str | None = None
    observaciones_admin: str | None = None
    fecha_envio: datetime | None = None
    fecha_evaluacion: datetime | None = None
    fecha_creacion: datetime
    total_items: int = 0


class PostulacionApplyResponse(BaseModel):
    """Response for applying/sending postulacion."""
    id_postulacion: int
    estado: PostulacionEstado
    puntaje_total: float | None = None
    mensaje: str


class PostulacionStatusUpdate(BaseModel):
    estado: PostulacionEstado
    observaciones_admin: str | None = None
