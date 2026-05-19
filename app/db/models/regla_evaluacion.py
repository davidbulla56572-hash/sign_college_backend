from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base
from app.db.models.hoja_vida import TipoItemHojaVida
from sqlalchemy import Enum as SAEnum


class ReglaEvaluacion(Base):
    __tablename__ = "reglas_evaluacion"

    id_regla: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_convocatoria: Mapped[int] = mapped_column(
        ForeignKey("convocatoria.id_convocatoria"),
        index=True,
    )
    tipo_item: Mapped[TipoItemHojaVida] = mapped_column(
        SAEnum(TipoItemHojaVida, name="tipo_item_hoja_vida"),
        nullable=False,
    )
    descripcion_regla: Mapped[str] = mapped_column(Text)
    puntaje_unitario: Mapped[float] = mapped_column(Numeric(8, 2))
    maximo_acumulable: Mapped[float | None] = mapped_column(Numeric(8, 2))
    unidad: Mapped[str] = mapped_column(String(80))

    convocatoria = relationship("Convocatoria", back_populates="reglas")
