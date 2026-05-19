from datetime import date

from pydantic import BaseModel, EmailStr, Field


class DocumentoProcesado(BaseModel):
    nombre_archivo: str
    tipo_archivo: str
    tamanio_bytes: int
    url_archivo: str


class DatosPersonalesHojaVida(BaseModel):
    nombre: str = ""
    apellido: str = ""
    email: EmailStr | None = None
    telefono: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    pais: str = "Colombia"


class HojaVidaItemPayload(BaseModel):
    descripcion: str = Field(min_length=1, max_length=2000)
    institucion: str | None = Field(default=None, max_length=180)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    cantidad: int | None = Field(default=None, ge=0)


class HojaVidaItemsPayload(BaseModel):
    formacion: list[HojaVidaItemPayload] = []
    experiencia: list[HojaVidaItemPayload] = []
    produccion: list[HojaVidaItemPayload] = []
    ponencia: list[HojaVidaItemPayload] = []
    investigacion: list[HojaVidaItemPayload] = []


class MetadataExtraccion(BaseModel):
    origen: str
    confidence: float | None = None
    warnings: list[str] = []


class HojaVidaProcesadaResponse(BaseModel):
    postulacion_id: int
    documento: DocumentoProcesado
    datos_personales: DatosPersonalesHojaVida
    items: HojaVidaItemsPayload
    metadata_extraccion: MetadataExtraccion


class HojaVidaSavePayload(BaseModel):
    documento: DocumentoProcesado | None = None
    datos_personales: DatosPersonalesHojaVida
    items: HojaVidaItemsPayload


class HojaVidaSaveResponse(BaseModel):
    id_postulacion: int
    estado: str
    total_items: int
    message: str


class HojaVidaDraftResponse(BaseModel):
    """Contract 8.16: persisted draft for rehydration."""
    id_postulacion: int
    id_convocatoria: int
    titulo_convocatoria: str
    estado: str
    url_cv_original: str | None = None
    datos_personales: DatosPersonalesHojaVida
    items: HojaVidaItemsPayload
