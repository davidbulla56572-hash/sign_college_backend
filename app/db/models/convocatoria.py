from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base


class Convocatoria(Base):
    __tablename__ = "convocatoria"

    id_convocatoria: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(180))
    descripcion: Mapped[str | None] = mapped_column(Text)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_cierre: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    activa: Mapped[bool] = mapped_column(default=True)
    creado_por: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"))
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    creador = relationship("Usuario", back_populates="convocatorias_creadas")
    postulaciones = relationship("Postulacion", back_populates="convocatoria")
    reglas = relationship("ReglaEvaluacion", back_populates="convocatoria")
