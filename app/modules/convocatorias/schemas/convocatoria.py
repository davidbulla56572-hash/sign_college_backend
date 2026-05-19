from datetime import datetime

from pydantic import BaseModel, Field


class ConvocatoriaCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=180)
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_cierre: datetime


class ConvocatoriaUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=3, max_length=180)
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None
    activa: bool | None = None


class ConvocatoriaResponse(BaseModel):
    id_convocatoria: int
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_cierre: datetime
    activa: bool
    creado_por: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime | None = None


class ConvocatoriaSummary(BaseModel):
    id_convocatoria: int
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_cierre: datetime
    activa: bool


class ConvocatoriaActivaResponse(BaseModel):
    """Contract 8.15: response for active convocatoria check."""
    hay_convocatoria_activa: bool
    convocatoria: ConvocatoriaSummary | None = None
    mensaje: str | None = None
