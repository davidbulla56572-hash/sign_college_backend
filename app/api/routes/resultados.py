from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.api.deps.auth import get_current_active_user, require_admin_role
from app.api.deps.db import get_db
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.db.models.user import Usuario
from app.core.exceptions import NotFoundError
from app.modules.evaluation.service import EvaluationService
from app.modules.results.schemas.resultado import (
    ConvocatoriaRef,
    DetalleItemResultado,
    DetalleResultadoResponse,
    DetalleSeccionResponse,
    MiResultadoResponse,
    RankingEntry,
    RankingResponse,
)

router = APIRouter()


def _get_eval_service(db: Session = Depends(get_db)) -> EvaluationService:
    return EvaluationService(db)


def _format_dt(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


# -- Aspirante endpoints --

@router.get("/mis-resultados", response_model=list[MiResultadoResponse])
def get_my_results(
    current_user: Usuario = Depends(get_current_active_user),
    eval_service: EvaluationService = Depends(_get_eval_service),
) -> list[MiResultadoResponse]:
    statement = (
        select(Postulacion)
        .where(Postulacion.id_usuario == current_user.id_usuario)
        .options(joinedload(Postulacion.convocatoria))
        .order_by(Postulacion.fecha_creacion.desc())
    )
    postulaciones = list(eval_service.db.scalars(statement).all())

    results: list[MiResultadoResponse] = []
    for p in postulaciones:
        items_stmt = (
            select(Postulacion.items_hoja_vida.property.mapper.class_)
            .where(
                __import__("sqlalchemy", fromlist=["Column"]).Column(
                    "id_postulacion"
                )
                == p.id_postulacion
            )
        )
        from app.db.models.hoja_vida import ItemHojaVida

        items = list(
            eval_service.db.scalars(
                select(ItemHojaVida).where(
                    ItemHojaVida.id_postulacion == p.id_postulacion
                )
            ).all()
        )

        titulo = p.convocatoria.titulo if p.convocatoria else ""
        results.append(
            MiResultadoResponse(
                id_postulacion=p.id_postulacion,
                estado=p.estado.value,
                puntaje_total=p.puntaje_total,
                fecha_evaluacion=_format_dt(p.fecha_evaluacion),
                convocatoria=ConvocatoriaRef(
                    id_convocatoria=p.id_convocatoria,
                    titulo=titulo,
                ),
                detalle=[
                    DetalleItemResultado(
                        id_item=item.id_item,
                        tipo_item=item.tipo_item.value,
                        descripcion=item.descripcion,
                        puntaje_asignado=item.puntaje_asignado or 0.0,
                    )
                    for item in items
                ],
            )
        )

    return results


@router.get("/{postulacion_id}", response_model=MiResultadoResponse)
def get_resultado_detalle(
    postulacion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    eval_service: EvaluationService = Depends(_get_eval_service),
) -> MiResultadoResponse:
    statement = (
        select(Postulacion)
        .where(
            Postulacion.id_postulacion == postulacion_id,
            Postulacion.id_usuario == current_user.id_usuario,
        )
        .options(joinedload(Postulacion.convocatoria))
    )
    postulacion = eval_service.db.scalar(statement)
    if postulacion is None:
        raise NotFoundError("Postulacion not found")

    from app.db.models.hoja_vida import ItemHojaVida

    items = list(
        eval_service.db.scalars(
            select(ItemHojaVida).where(
                ItemHojaVida.id_postulacion == postulacion_id
            )
        ).all()
    )

    titulo = postulacion.convocatoria.titulo if postulacion.convocatoria else ""

    return MiResultadoResponse(
        id_postulacion=postulacion.id_postulacion,
        estado=postulacion.estado.value,
        puntaje_total=postulacion.puntaje_total,
        fecha_evaluacion=_format_dt(postulacion.fecha_evaluacion),
        convocatoria=ConvocatoriaRef(
            id_convocatoria=postulacion.id_convocatoria,
            titulo=titulo,
        ),
        detalle=[
            DetalleItemResultado(
                id_item=item.id_item,
                tipo_item=item.tipo_item.value,
                descripcion=item.descripcion,
                puntaje_asignado=item.puntaje_asignado or 0.0,
            )
            for item in items
        ],
    )


# -- Admin endpoints --

@router.get(
    "/ranking/{convocatoria_id}",
    response_model=RankingResponse,
)
def get_ranking(
    convocatoria_id: int,
    _: Usuario = Depends(require_admin_role),
    eval_service: EvaluationService = Depends(_get_eval_service),
) -> RankingResponse:
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
)
def evaluar_postulacion(
    postulacion_id: int,
    _: Usuario = Depends(require_admin_role),
    eval_service: EvaluationService = Depends(_get_eval_service),
) -> MiResultadoResponse:
    result = eval_service.apply_evaluation(postulacion_id)

    # Fetch the updated postulacion
    from sqlalchemy.orm import joinedload

    statement = (
        select(Postulacion)
        .where(Postulacion.id_postulacion == postulacion_id)
        .options(joinedload(Postulacion.convocatoria))
    )
    postulacion = eval_service.db.scalar(statement)
    if postulacion is None:
        raise NotFoundError("Postulacion not found")

    from app.db.models.hoja_vida import ItemHojaVida

    items = list(
        eval_service.db.scalars(
            select(ItemHojaVida).where(
                ItemHojaVida.id_postulacion == postulacion_id
            )
        ).all()
    )

    titulo = postulacion.convocatoria.titulo if postulacion.convocatoria else ""

    return MiResultadoResponse(
        id_postulacion=postulacion.id_postulacion,
        estado=postulacion.estado.value,
        puntaje_total=result.puntaje_total,
        fecha_evaluacion=_format_dt(postulacion.fecha_evaluacion),
        convocatoria=ConvocatoriaRef(
            id_convocatoria=postulacion.id_convocatoria,
            titulo=titulo,
        ),
        detalle=[
            DetalleItemResultado(
                id_item=d.id_item,
                tipo_item=d.tipo_item.value,
                descripcion=d.descripcion,
                puntaje_asignado=d.puntaje_asignado,
            )
            for d in result.item_detalles
        ],
    )
