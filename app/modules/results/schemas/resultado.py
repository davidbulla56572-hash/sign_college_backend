from datetime import datetime

from pydantic import BaseModel


class ConvocatoriaRef(BaseModel):
    id_convocatoria: int
    titulo: str


class DetalleItemResultado(BaseModel):
    id_item: int
    tipo_item: str
    descripcion: str
    puntaje_asignado: float


class DetalleSeccionResponse(BaseModel):
    tipo_item: str
    descripcion_regla: str
    cantidad_items: int
    puntaje_unitario: float
    puntaje_bruto: float
    maximo_acumulable: float | None
    puntaje_final: float


class MiResultadoResponse(BaseModel):
    """Contrato 5.16: resultado del aspirante."""
    id_postulacion: int
    estado: str
    puntaje_total: float | None
    fecha_evaluacion: str | None = None
    convocatoria: ConvocatoriaRef
    detalle: list[DetalleItemResultado]


class RankingEntry(BaseModel):
    id_postulacion: int
    id_usuario: int
    aspirante: str
    cedula: str
    estado: str
    puntaje_total: float | None
    convocatoria: str
    fecha_evaluacion: str | None = None


class RankingResponse(BaseModel):
    """Contrato 5.17: ranking administrativo."""
    id_convocatoria: int
    titulo_convocatoria: str
    items: list[RankingEntry]
    total: int


class DetalleResultadoResponse(BaseModel):
    """Detalle completo de evaluacion (admin)."""
    id_postulacion: int
    id_usuario: int
    nombre_aspirante: str
    apellido_aspirante: str
    titulo_convocatoria: str
    estado: str
    puntaje_total: float | None
    desglose: list[DetalleSeccionResponse]
    fecha_envio: str | None = None
    fecha_evaluacion: str | None = None
    observaciones_admin: str | None = None
