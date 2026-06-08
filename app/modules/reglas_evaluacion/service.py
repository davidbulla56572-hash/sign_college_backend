from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.convocatoria import ConvocatoriaEstado
from app.db.models.regla_evaluacion import ReglaEvaluacion
from app.modules.convocatorias.repository import ConvocatoriaRepository
from app.modules.reglas_evaluacion.repository import ReglaEvaluacionRepository
from app.modules.reglas_evaluacion.schemas.regla_evaluacion import (
    ReglaEvaluacionCreate,
    ReglaEvaluacionUpdate,
)


class ReglaEvaluacionService:
    def __init__(self, repository: ReglaEvaluacionRepository) -> None:
        self.repository = repository
        self.convocatoria_repository = ConvocatoriaRepository(repository.db)

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
        convocatoria = self.convocatoria_repository.get_by_id(convocatoria_id)
        if convocatoria is None:
            raise NotFoundError("Convocatoria not found")
        if convocatoria.estado == ConvocatoriaEstado.CERRADA:
            raise ConflictError("No se pueden crear reglas en una convocatoria cerrada")
        existing = self.repository.get_by_convocatoria_and_tipo(
            convocatoria_id, data.tipo_item
        )
        if existing is not None:
            raise ConflictError("Ya existe una regla para ese tipo de item")
        regla = self.repository.create(data, convocatoria_id)
        self.repository.commit()
        return regla

    def update(
        self,
        regla_id: int,
        data: ReglaEvaluacionUpdate,
    ) -> ReglaEvaluacion:
        regla = self.get_by_id(regla_id)
        convocatoria = self.convocatoria_repository.get_by_id(regla.id_convocatoria)
        if convocatoria is None:
            raise NotFoundError("Convocatoria not found")
        if convocatoria.estado == ConvocatoriaEstado.CERRADA:
            raise ConflictError("No se pueden editar reglas de una convocatoria cerrada")
        if data.tipo_item is not None and data.tipo_item != regla.tipo_item:
            existing = self.repository.get_by_convocatoria_and_tipo(
                regla.id_convocatoria, data.tipo_item
            )
            if existing is not None and existing.id_regla != regla.id_regla:
                raise ConflictError("Ya existe una regla para ese tipo de item")
        updated = self.repository.update(regla, data)
        self.repository.commit()
        return updated

    def delete(self, regla_id: int) -> None:
        regla = self.get_by_id(regla_id)
        convocatoria = self.convocatoria_repository.get_by_id(regla.id_convocatoria)
        if convocatoria is None:
            raise NotFoundError("Convocatoria not found")
        if convocatoria.estado == ConvocatoriaEstado.CERRADA:
            raise ConflictError("No se pueden eliminar reglas de una convocatoria cerrada")
        self.repository.delete(regla)
        self.repository.commit()
