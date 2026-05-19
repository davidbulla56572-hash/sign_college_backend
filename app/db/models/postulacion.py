from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base


class PostulacionEstado(str, Enum):
    BORRADOR = "BORRADOR"
    ENVIADA = "ENVIADA"
    EN_EVALUACION = "EN_EVALUACION"
    EVALUADA = "EVALUADA"
    RECHAZADA = "RECHAZADA"


class Postulacion(Base):
    __tablename__ = "postulaciones"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario",
            "id_convocatoria",
            name="uq_postulacion_usuario_convocatoria",
        ),
    )

    id_postulacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), index=True)
    id_convocatoria: Mapped[int] = mapped_column(
        ForeignKey("convocatorias.id_convocatoria"),
        index=True,
    )
    estado: Mapped[PostulacionEstado] = mapped_column(
        SAEnum(PostulacionEstado, name="postulacion_estado"),
        default=PostulacionEstado.BORRADOR,
        nullable=False,
    )
    puntaje_total: Mapped[float | None] = mapped_column(Numeric(8, 2))
    url_cv_original: Mapped[str | None] = mapped_column(String(500))
    observaciones_admin: Mapped[str | None] = mapped_column(Text)
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_evaluacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    usuario = relationship("Usuario", back_populates="postulaciones")
    convocatoria = relationship("Convocatoria", back_populates="postulaciones")
    items_hoja_vida = relationship("ItemHojaVida", back_populates="postulacion")
