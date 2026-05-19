from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models.regla_evaluacion import ReglaEvaluacion
from app.modules.reglas_evaluacion.schemas.regla_evaluacion import (
    ReglaEvaluacionCreate,
    ReglaEvaluacionUpdate,
)


class ReglaEvaluacionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, regla_id: int) -> ReglaEvaluacion | None:
        statement = select(ReglaEvaluacion).where(
            ReglaEvaluacion.id_regla == regla_id
        )
        return self.db.scalar(statement)

    def list_by_convocatoria(self, convocatoria_id: int) -> list[ReglaEvaluacion]:
        statement = (
            select(ReglaEvaluacion)
            .where(ReglaEvaluacion.id_convocatoria == convocatoria_id)
            .order_by(ReglaEvaluacion.tipo_item)
        )
        return list(self.db.scalars(statement).all())

    def get_by_convocatoria_and_tipo(
        self,
        convocatoria_id: int,
        tipo_item: object,
    ) -> ReglaEvaluacion | None:
        statement = select(ReglaEvaluacion).where(
            ReglaEvaluacion.id_convocatoria == convocatoria_id,
            ReglaEvaluacion.tipo_item == tipo_item,
        )
        return self.db.scalar(statement)

    def create(
        self,
        data: ReglaEvaluacionCreate,
        convocatoria_id: int,
    ) -> ReglaEvaluacion:
        regla = ReglaEvaluacion(
            id_convocatoria=convocatoria_id,
            tipo_item=data.tipo_item,
            descripcion_regla=data.descripcion_regla,
            puntaje_unitario=data.puntaje_unitario,
            maximo_acumulable=data.maximo_acumulable,
            unidad=data.unidad,
        )
        self.db.add(regla)
        self.db.flush()
        return regla

    def update(
        self,
        regla: ReglaEvaluacion,
        data: ReglaEvaluacionUpdate,
    ) -> ReglaEvaluacion:
        if data.tipo_item is not None:
            regla.tipo_item = data.tipo_item
        if data.descripcion_regla is not None:
            regla.descripcion_regla = data.descripcion_regla
        if data.puntaje_unitario is not None:
            regla.puntaje_unitario = data.puntaje_unitario
        if data.maximo_acumulable is not None:
            regla.maximo_acumulable = data.maximo_acumulable
        if data.unidad is not None:
            regla.unidad = data.unidad
        self.db.flush()
        return regla

    def delete(self, regla: ReglaEvaluacion) -> None:
        self.db.delete(regla)

    def delete_by_convocatoria(self, convocatoria_id: int) -> int:
        result = self.db.execute(
            delete(ReglaEvaluacion).where(
                ReglaEvaluacion.id_convocatoria == convocatoria_id
            )
        )
        return result.rowcount

    def commit(self) -> None:
        self.db.commit()
