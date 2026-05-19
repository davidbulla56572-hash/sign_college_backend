from datetime import datetime

from pydantic import BaseModel

from app.db.models.postulacion import PostulacionEstado


class PostulacionSummary(BaseModel):
    id_postulacion: int
    id_convocatoria: int
    estado: PostulacionEstado
    puntaje_total: float | None = None
    fecha_envio: datetime | None = None
