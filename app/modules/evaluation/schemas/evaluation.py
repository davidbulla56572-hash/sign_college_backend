from pydantic import BaseModel

from app.db.models.hoja_vida import TipoItemHojaVida


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


class EvaluationResult(BaseModel):
    """Resultado completo de la evaluacion de una postulacion."""
    postulacion_id: int
    puntaje_total: float
    desglose: list[DetalleSeccion]
    item_detalles: list[ItemEvaluadoDetalle]
    reglas_aplicadas: int
    items_evaluados: int
