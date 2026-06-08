from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.db.models.convocatoria import ConvocatoriaEstado


class ConvocatoriaCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=180)
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_cierre: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "ConvocatoriaCreate":
        if self.fecha_cierre < self.fecha_inicio:
            raise ValueError("fecha_cierre no puede ser anterior a fecha_inicio")
        return self


class ConvocatoriaUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=3, max_length=180)
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None
    activa: bool | None = None
    estado: ConvocatoriaEstado | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "ConvocatoriaUpdate":
        if (
            self.fecha_inicio is not None
            and self.fecha_cierre is not None
            and self.fecha_cierre < self.fecha_inicio
        ):
            raise ValueError("fecha_cierre no puede ser anterior a fecha_inicio")
        return self


class ConvocatoriaResponse(BaseModel):
    id_convocatoria: int
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_cierre: datetime
    estado: ConvocatoriaEstado
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
    estado: ConvocatoriaEstado
    activa: bool


class ConvocatoriaActivaResponse(BaseModel):
    """Contract 8.15: response for active convocatoria check."""
    hay_convocatoria_activa: bool
    convocatoria: ConvocatoriaSummary | None = None
    mensaje: str | None = None
