from datetime import datetime

from pydantic import BaseModel


class ConvocatoriaSummary(BaseModel):
    id_convocatoria: int
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_cierre: datetime
    activa: bool
