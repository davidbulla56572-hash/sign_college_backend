from fastapi import APIRouter, Depends

from app.api.deps.auth import require_admin_role
from app.api.deps.db import get_db
from app.db.models.user import Usuario
from app.modules.reglas_evaluacion.repository import ReglaEvaluacionRepository
from app.modules.reglas_evaluacion.schemas.regla_evaluacion import (
    ReglaEvaluacionCreate,
    ReglaEvaluacionResponse,
    ReglaEvaluacionUpdate,
)
from app.modules.reglas_evaluacion.service import ReglaEvaluacionService

router = APIRouter()


def _get_service(db: object = Depends(get_db)) -> ReglaEvaluacionService:
    repo = ReglaEvaluacionRepository(db)  # type: ignore[arg-type]
    return ReglaEvaluacionService(repo)


def _to_response(regla: object) -> ReglaEvaluacionResponse:
    return ReglaEvaluacionResponse(
        id_regla=regla.id_regla,  # type: ignore[attr-defined]
        id_convocatoria=regla.id_convocatoria,  # type: ignore[attr-defined]
        tipo_item=regla.tipo_item,  # type: ignore[attr-defined]
        descripcion_regla=regla.descripcion_regla,  # type: ignore[attr-defined]
        puntaje_unitario=regla.puntaje_unitario,  # type: ignore[attr-defined]
        maximo_acumulable=regla.maximo_acumulable,  # type: ignore[attr-defined]
        unidad=regla.unidad,  # type: ignore[attr-defined]
    )


@router.get(
    "/convocatorias/{convocatoria_id}",
    response_model=list[ReglaEvaluacionResponse],
)
def list_reglas(
    convocatoria_id: int,
    _: Usuario = Depends(require_admin_role),
    service: ReglaEvaluacionService = Depends(_get_service),
) -> list[ReglaEvaluacionResponse]:
    reglas = service.list_by_convocatoria(convocatoria_id)
    return [_to_response(r) for r in reglas]


@router.post(
    "/convocatorias/{convocatoria_id}",
    response_model=ReglaEvaluacionResponse,
    status_code=201,
)
def create_regla(
    convocatoria_id: int,
    payload: ReglaEvaluacionCreate,
    _: Usuario = Depends(require_admin_role),
    service: ReglaEvaluacionService = Depends(_get_service),
) -> ReglaEvaluacionResponse:
    regla = service.create(convocatoria_id, payload)
    return _to_response(regla)


@router.patch(
    "/{regla_id}",
    response_model=ReglaEvaluacionResponse,
)
def update_regla(
    regla_id: int,
    payload: ReglaEvaluacionUpdate,
    _: Usuario = Depends(require_admin_role),
    service: ReglaEvaluacionService = Depends(_get_service),
) -> ReglaEvaluacionResponse:
    regla = service.update(regla_id, payload)
    return _to_response(regla)


@router.delete("/{regla_id}", status_code=204)
def delete_regla(
    regla_id: int,
    _: Usuario = Depends(require_admin_role),
    service: ReglaEvaluacionService = Depends(_get_service),
) -> None:
    service.delete(regla_id)
