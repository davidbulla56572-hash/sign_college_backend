from pydantic import BaseModel, Field

from app.db.models.hoja_vida import TipoItemHojaVida


class ReglaAplicadaInfo(BaseModel):
    """Informacion de la regla aplicada a un item (14.17)."""
    id_regla: int
    descripcion_regla: str


class ItemEvaluadoDetalle(BaseModel):
    """Detalle de puntaje asignado a un item individual."""
    id_item: int
    tipo_item: TipoItemHojaVida
    descripcion: str
    puntaje_asignado: float


class DetalleSeccion(BaseModel):
    """Agregacion de puntaje por tipo de item (seccion)."""
    tipo_item: TipoItemHojaVida
    descripcion_regla: str
    cantidad_items: int
    puntaje_unitario: float
    puntaje_bruto: float
    maximo_acumulable: float | None
    puntaje_final: float


class EvaluationTraceItem(BaseModel):
    """Contract 14.17: trazabilidad por item con regla aplicada."""
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
    """Contract 14.17: respuesta completa de trazabilidad."""
    id_postulacion: int
    id_convocatoria: int
    puntaje_total: float
    detalle_evaluacion: list[EvaluationTraceItem]
    advertencias: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    """Resultado completo de la evaluacion de una postulacion."""
    postulacion_id: int
    id_convocatoria: int
    puntaje_total: float
    desglose: list[DetalleSeccion]
    item_detalles: list[ItemEvaluadoDetalle]
    reglas_aplicadas: int
    items_evaluados: int
    items_sin_regla: int = 0
    advertencias: list[str] = Field(default_factory=list)
