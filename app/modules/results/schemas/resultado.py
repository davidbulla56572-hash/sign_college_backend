from datetime import datetime

from pydantic import BaseModel, Field


# -- Fase 15: Estado de postulacion --

class PostulacionStatusResponse(BaseModel):
    """Estado legible de una postulacion para el aspirante (15.15)."""
    id_postulacion: int
    estado: str
    estado_label: str
    estado_color: str
    mensaje_contextual: str
    id_convocatoria: int
    titulo_convocatoria: str
    fecha_envio: str | None = None
    fecha_evaluacion: str | None = None


# -- Fase 15: Resumen de evaluacion por seccion --

class ResumenEvaluacion(BaseModel):
    """Resumen de puntaje agrupado por tipo de item (15.16)."""
    tipo_item: str
    label: str
    puntaje_obtenido: float
    cantidad_items: int


# -- Fase 15: Resultado del aspirante --

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
    """Contrato 15.16: resultado del aspirante con contexto y resumen."""
    id_postulacion: int
    estado: str
    estado_label: str
    estado_color: str
    mensaje_contextual: str
    puntaje_total: float | None
    fecha_evaluacion: str | None = None
    convocatoria: ConvocatoriaRef
    resumen_evaluacion: list[ResumenEvaluacion] = Field(default_factory=list)
    detalle: list[DetalleItemResultado] = Field(default_factory=list)


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
