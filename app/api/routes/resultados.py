"""Endpoints de resultados para el aspirante (Fase 15) y admin."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_active_user, require_admin_role
from app.api.deps.db import get_db
from app.db.models.user import Usuario
from app.modules.evaluation.service import EvaluationService
from app.modules.results.schemas.resultado import (
    MiResultadoResponse,
    PostulacionStatusResponse,
    RankingEntry,
    RankingResponse,
)
from app.modules.results.service import ResultsService

router = APIRouter()


def _get_results_service(db: Session = Depends(get_db)) -> ResultsService:
    return ResultsService(db)


def _get_eval_service(db: Session = Depends(get_db)) -> EvaluationService:
    return EvaluationService(db)


# ============================================================
# Aspirante endpoints (Fase 15)
# ============================================================


@router.get(
    "/mis-resultados",
    response_model=list[MiResultadoResponse],
    summary="Mis resultados (15.15)",
)
def get_mis_resultados(
    current_user: Usuario = Depends(get_current_active_user),
    service: ResultsService = Depends(_get_results_service),
) -> list[MiResultadoResponse]:
    """Lista de resultados del aspirante con contexto completo (15.16)."""
    return service.get_mis_resultados(current_user.id_usuario)


@router.get(
    "/postulaciones/{postulacion_id}",
    response_model=MiResultadoResponse,
    summary="Detalle de una postulacion (15.15)",
)
def get_resultado_detalle(
    postulacion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: ResultsService = Depends(_get_results_service),
) -> MiResultadoResponse:
    """Detalle de resultado de una postulacion especifica."""
    return service.get_resultado_detalle(postulacion_id, current_user.id_usuario)


@router.get(
    "/postulaciones/{postulacion_id}/status",
    response_model=PostulacionStatusResponse,
    summary="Estado legible de una postulacion (15.15)",
)
def get_postulacion_status(
    postulacion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: ResultsService = Depends(_get_results_service),
) -> PostulacionStatusResponse:
    """Devuelve el estado legible de una postulacion con mensaje contextual."""
    return service.get_postulacion_status(postulacion_id, current_user.id_usuario)


# ============================================================
# Admin endpoints (legacy, preserved for backward compatibility)
# ============================================================


def _format_dt(dt) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


@router.get(
    "/ranking/{convocatoria_id}",
    response_model=RankingResponse,
    summary="Ranking de una convocatoria",
)
def get_ranking(
    convocatoria_id: int,
    _: Usuario = Depends(require_admin_role),
    eval_service: EvaluationService = Depends(_get_eval_service),
) -> RankingResponse:
    """Ranking de todas las postulaciones evaluadas en una convocatoria."""
    data = eval_service.evaluate_convocatoria_ranking(convocatoria_id)

    entries = [
        RankingEntry(
            id_postulacion=r["id_postulacion"],
            id_usuario=r["id_usuario"],
            aspirante=r["aspirante"],
            cedula=r["cedula"],
            estado=r["estado"],
            puntaje_total=r["puntaje_total"],
            convocatoria=r["convocatoria"],
            fecha_evaluacion=_format_dt(r["fecha_evaluacion"]),
        )
        for r in data["items"]
    ]

    return RankingResponse(
        id_convocatoria=data["id_convocatoria"],
        titulo_convocatoria=data["titulo_convocatoria"],
        items=entries,
        total=data["total"],
    )


@router.post(
    "/{postulacion_id}/evaluar",
    response_model=MiResultadoResponse,
    summary="Evaluar una postulacion (legacy)",
)
def evaluar_postulacion(
    postulacion_id: int,
    _: Usuario = Depends(require_admin_role),
    eval_service: EvaluationService = Depends(_get_eval_service),
    results_service: ResultsService = Depends(_get_results_service),
) -> MiResultadoResponse:
    """Evalua una postulacion y devuelve el resultado (legacy)."""
    from app.db.models.postulacion import Postulacion
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload

    result = eval_service.apply_evaluation(postulacion_id)

    statement = (
        select(Postulacion)
        .where(Postulacion.id_postulacion == postulacion_id)
        .options(joinedload(Postulacion.convocatoria))
    )
    postulacion = eval_service.db.scalar(statement)
    if postulacion is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Postulacion not found")

    titulo = postulacion.convocatoria.titulo if postulacion.convocatoria else ""

    from app.db.models.hoja_vida import ItemHojaVida

    items = list(
        eval_service.db.scalars(
            select(ItemHojaVida).where(
                ItemHojaVida.id_postulacion == postulacion_id
            )
        ).all()
    )

    return MiResultadoResponse(
        id_postulacion=postulacion.id_postulacion,
        estado=postulacion.estado.value,
        estado_label="Evaluada",
        estado_color="green",
        mensaje_contextual="Tu postulacion ha sido evaluada.",
        puntaje_total=result.puntaje_total,
        fecha_evaluacion=_format_dt(postulacion.fecha_evaluacion),
        convocatoria={
            "id_convocatoria": postulacion.id_convocatoria,
            "titulo": titulo,
        },
        resumen_evaluacion=[],
        detalle=[
            {
                "id_item": d.id_item,
                "tipo_item": d.tipo_item.value,
                "descripcion": d.descripcion,
                "puntaje_asignado": d.puntaje_asignado,
            }
            for d in result.item_detalles
        ],
    )
