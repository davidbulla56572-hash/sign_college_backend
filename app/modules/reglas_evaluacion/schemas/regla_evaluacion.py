from pydantic import BaseModel, Field

from app.db.models.hoja_vida import TipoItemHojaVida


class ReglaEvaluacionCreate(BaseModel):
    tipo_item: TipoItemHojaVida
    descripcion_regla: str = Field(..., min_length=3, max_length=2000)
    puntaje_unitario: float = Field(..., ge=0)
    maximo_acumulable: float | None = Field(None, ge=0)
    unidad: str = Field(..., min_length=1, max_length=80)


class ReglaEvaluacionUpdate(BaseModel):
    tipo_item: TipoItemHojaVida | None = None
    descripcion_regla: str | None = Field(None, min_length=3, max_length=2000)
    puntaje_unitario: float | None = Field(None, ge=0)
    maximo_acumulable: float | None = Field(None, ge=0)
    unidad: str | None = Field(None, min_length=1, max_length=80)


class ReglaEvaluacionResponse(BaseModel):
    id_regla: int
    id_convocatoria: int
    tipo_item: TipoItemHojaVida
    descripcion_regla: str
    puntaje_unitario: float
    maximo_acumulable: float | None
    unidad: str
