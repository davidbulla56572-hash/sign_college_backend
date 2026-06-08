from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.convocatoria import Convocatoria, ConvocatoriaEstado
from app.modules.convocatorias.schemas.convocatoria import (
    ConvocatoriaCreate,
    ConvocatoriaUpdate,
)


class ConvocatoriaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, convocatoria_id: int) -> Convocatoria | None:
        statement = select(Convocatoria).where(
            Convocatoria.id_convocatoria == convocatoria_id
        )
        return self.db.scalar(statement)

    def list_all(self) -> list[Convocatoria]:
        statement = (
            select(Convocatoria)
            .order_by(Convocatoria.fecha_creacion.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_activas(self) -> list[Convocatoria]:
        statement = (
            select(Convocatoria)
            .where(
                Convocatoria.activa.is_(True),
                Convocatoria.estado == ConvocatoriaEstado.ACTIVA,
            )
            .order_by(Convocatoria.fecha_inicio.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_active(self) -> Convocatoria | None:
        statement = (
            select(Convocatoria)
            .where(
                Convocatoria.activa.is_(True),
                Convocatoria.estado == ConvocatoriaEstado.ACTIVA,
            )
            .limit(1)
        )
        return self.db.scalar(statement)

    def create(self, data: ConvocatoriaCreate, creado_por: int) -> Convocatoria:
        convocatoria = Convocatoria(
            titulo=data.titulo,
            descripcion=data.descripcion,
            fecha_inicio=data.fecha_inicio,
            fecha_cierre=data.fecha_cierre,
            creado_por=creado_por,
            estado=ConvocatoriaEstado.BORRADOR,
            activa=False,
        )
        self.db.add(convocatoria)
        self.db.flush()
        return convocatoria

    def update(
        self,
        convocatoria: Convocatoria,
        data: ConvocatoriaUpdate,
    ) -> Convocatoria:
        if data.titulo is not None:
            convocatoria.titulo = data.titulo
        if data.descripcion is not None:
            convocatoria.descripcion = data.descripcion
        if data.fecha_inicio is not None:
            convocatoria.fecha_inicio = data.fecha_inicio
        if data.fecha_cierre is not None:
            convocatoria.fecha_cierre = data.fecha_cierre
        if data.estado is not None:
            convocatoria.estado = data.estado
        if data.activa is not None:
            convocatoria.activa = data.activa
        self.db.flush()
        return convocatoria

    def deactivate_current_active(self, keep_convocatoria_id: int | None = None) -> None:
        statement = select(Convocatoria).where(
            Convocatoria.activa.is_(True),
            Convocatoria.estado == ConvocatoriaEstado.ACTIVA,
        )
        if keep_convocatoria_id is not None:
            statement = statement.where(
                Convocatoria.id_convocatoria != keep_convocatoria_id
            )
        for convocatoria in self.db.scalars(statement).all():
            convocatoria.activa = False
            convocatoria.estado = ConvocatoriaEstado.BORRADOR
        self.db.flush()

    def delete(self, convocatoria: Convocatoria) -> None:
        self.db.delete(convocatoria)

    def commit(self) -> None:
        self.db.commit()
