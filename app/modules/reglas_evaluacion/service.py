from app.core.exceptions import NotFoundError
from app.db.models.regla_evaluacion import ReglaEvaluacion
from app.modules.reglas_evaluacion.repository import ReglaEvaluacionRepository
from app.modules.reglas_evaluacion.schemas.regla_evaluacion import (
    ReglaEvaluacionCreate,
    ReglaEvaluacionUpdate,
)


class ReglaEvaluacionService:
    def __init__(self, repository: ReglaEvaluacionRepository) -> None:
        self.repository = repository

    def list_by_convocatoria(self, convocatoria_id: int) -> list[ReglaEvaluacion]:
        return self.repository.list_by_convocatoria(convocatoria_id)

    def get_by_id(self, regla_id: int) -> ReglaEvaluacion:
        regla = self.repository.get_by_id(regla_id)
        if regla is None:
            raise NotFoundError("Regla de evaluacion not found")
        return regla

    def create(
        self,
        convocatoria_id: int,
        data: ReglaEvaluacionCreate,
    ) -> ReglaEvaluacion:
        regla = self.repository.create(data, convocatoria_id)
        self.repository.commit()
        return regla

    def update(
        self,
        regla_id: int,
        data: ReglaEvaluacionUpdate,
    ) -> ReglaEvaluacion:
        regla = self.get_by_id(regla_id)
        updated = self.repository.update(regla, data)
        self.repository.commit()
        return updated

    def delete(self, regla_id: int) -> None:
        regla = self.get_by_id(regla_id)
        self.repository.delete(regla)
        self.repository.commit()
