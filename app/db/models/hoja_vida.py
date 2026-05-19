from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base


class TipoItemHojaVida(str, Enum):
    FORMACION = "FORMACION"
    EXPERIENCIA = "EXPERIENCIA"
    PRODUCCION = "PRODUCCION"
    DOCUMENTO = "DOCUMENTO"
    OTRO = "OTRO"


class ItemHojaVida(Base):
    __tablename__ = "items_hoja_vida"

    id_item: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_postulacion: Mapped[int] = mapped_column(
        ForeignKey("postulaciones.id_postulacion"),
        index=True,
    )
    tipo_item: Mapped[TipoItemHojaVida] = mapped_column(
        SAEnum(TipoItemHojaVida, name="tipo_item_hoja_vida"),
        nullable=False,
    )
    descripcion: Mapped[str] = mapped_column(Text)
    institucion: Mapped[str | None] = mapped_column(String(180))
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    cantidad: Mapped[int | None] = mapped_column(Integer)
    puntaje_asignado: Mapped[float | None] = mapped_column(Numeric(8, 2))
    validado: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    postulacion = relationship("Postulacion", back_populates="items_hoja_vida")
    soportes = relationship("SoporteItem", back_populates="item")


class SoporteItem(Base):
    __tablename__ = "soportes_item"

    id_soporte: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_item: Mapped[int] = mapped_column(ForeignKey("items_hoja_vida.id_item"), index=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    url_archivo: Mapped[str] = mapped_column(String(500))
    tipo_archivo: Mapped[str] = mapped_column(String(120))
    tamanio_bytes: Mapped[int] = mapped_column(Integer)
    fecha_carga: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    item = relationship("ItemHojaVida", back_populates="soportes")
