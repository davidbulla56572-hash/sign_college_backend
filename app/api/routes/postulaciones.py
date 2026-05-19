from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_active_user, require_admin_role
from app.api.deps.db import get_db
from app.db.models.user import Usuario
from app.modules.postulaciones.repository import PostulacionRepository
from app.modules.postulaciones.schemas.postulacion import (
    ActiveDraftResponse,
    PostulacionApplyResponse,
    PostulacionCreate,
    PostulacionDetail,
    PostulacionStatusUpdate,
    PostulacionSummary,
)
from app.modules.postulaciones.service import PostulacionService

router = APIRouter()


def _get_service(db: object = Depends(get_db)) -> PostulacionService:
    repo = PostulacionRepository(db)  # type: ignore[arg-type]
    return PostulacionService(repo)


def _to_summary(p: object) -> PostulacionSummary:
    titulo = None
    if hasattr(p, "convocatoria") and p.convocatoria:  # type: ignore[attr-defined]
        titulo = p.convocatoria.titulo  # type: ignore[attr-defined]
    return PostulacionSummary(
        id_postulacion=p.id_postulacion,  # type: ignore[attr-defined]
        id_convocatoria=p.id_convocatoria,  # type: ignore[attr-defined]
        titulo_convocatoria=titulo,
        estado=p.estado,  # type: ignore[attr-defined]
        puntaje_total=p.puntaje_total,  # type: ignore[attr-defined]
        fecha_envio=p.fecha_envio,  # type: ignore[attr-defined]
    )


def _to_detail(p: object, total_items: int = 0) -> PostulacionDetail:
    titulo = None
    if hasattr(p, "convocatoria") and p.convocatoria:  # type: ignore[attr-defined]
        titulo = p.convocatoria.titulo  # type: ignore[attr-defined]
    return PostulacionDetail(
        id_postulacion=p.id_postulacion,  # type: ignore[attr-defined]
        id_usuario=p.id_usuario,  # type: ignore[attr-defined]
        id_convocatoria=p.id_convocatoria,  # type: ignore[attr-defined]
        titulo_convocatoria=titulo,
        estado=p.estado,  # type: ignore[attr-defined]
        puntaje_total=p.puntaje_total,  # type: ignore[attr-defined]
        url_cv_original=p.url_cv_original,  # type: ignore[attr-defined]
        observaciones_admin=p.observaciones_admin,  # type: ignore[attr-defined]
        fecha_envio=p.fecha_envio,  # type: ignore[attr-defined]
        fecha_evaluacion=p.fecha_evaluacion,  # type: ignore[attr-defined]
        fecha_creacion=p.fecha_creacion,  # type: ignore[attr-defined]
        total_items=total_items,
    )


# -- Aspirante endpoints --

@router.post("/active-draft", response_model=ActiveDraftResponse)
def get_or_create_active_draft(
    current_user: Usuario = Depends(get_current_active_user),
    service: PostulacionService = Depends(_get_service),
) -> ActiveDraftResponse:
    """Create or recover draft postulacion for the active convocatoria."""
    return service.get_or_create_active_draft(current_user.id_usuario)


@router.patch("/mine/{postulacion_id}/apply", response_model=PostulacionApplyResponse)
def apply_postulacion(
    postulacion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: PostulacionService = Depends(_get_service),
) -> PostulacionApplyResponse:
    """Apply/send the postulacion."""
    return service.apply(postulacion_id, current_user.id_usuario)

@router.post("", response_model=PostulacionDetail, status_code=201)
def create_postulacion(
    payload: PostulacionCreate,
    current_user: Usuario = Depends(get_current_active_user),
    service: PostulacionService = Depends(_get_service),
) -> PostulacionDetail:
    postulacion = service.create_for_user(current_user.id_usuario, payload)
    total_items = service.repository.count_items(postulacion.id_postulacion)
    return _to_detail(postulacion, total_items)


@router.get("/mine", response_model=list[PostulacionSummary])
def list_my_postulaciones(
    current_user: Usuario = Depends(get_current_active_user),
    service: PostulacionService = Depends(_get_service),
) -> list[PostulacionSummary]:
    postulaciones = service.list_for_user(current_user.id_usuario)
    return [_to_summary(p) for p in postulaciones]


@router.get("/mine/{postulacion_id}", response_model=PostulacionDetail)
def get_my_postulacion(
    postulacion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: PostulacionService = Depends(_get_service),
) -> PostulacionDetail:
    postulacion = service.get_for_user(
        postulacion_id, current_user.id_usuario
    )
    total_items = service.repository.count_items(postulacion_id)
    return _to_detail(postulacion, total_items)


@router.post("/mine/{postulacion_id}/submit", response_model=PostulacionDetail)
def submit_postulacion(
    postulacion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: PostulacionService = Depends(_get_service),
) -> PostulacionDetail:
    postulacion = service.submit(postulacion_id, current_user.id_usuario)
    total_items = service.repository.count_items(postulacion_id)
    return _to_detail(postulacion, total_items)


# -- Admin endpoints --

@router.get("/todas", response_model=list[PostulacionSummary])
def list_all_postulaciones(
    estado: str | None = None,
    _: Usuario = Depends(require_admin_role),
    service: PostulacionService = Depends(_get_service),
) -> list[PostulacionSummary]:
    from app.db.models.postulacion import PostulacionEstado

    estado_enum = None
    if estado:
        try:
            estado_enum = PostulacionEstado(estado.upper())
        except ValueError:
            pass
    postulaciones = service.list_all(estado_enum)
    return [_to_summary(p) for p in postulaciones]


@router.get("/{postulacion_id}", response_model=PostulacionDetail)
def get_postulacion(
    postulacion_id: int,
    _: Usuario = Depends(require_admin_role),
    service: PostulacionService = Depends(_get_service),
) -> PostulacionDetail:
    postulacion = service.get_by_id(postulacion_id)
    total_items = service.repository.count_items(postulacion_id)
    return _to_detail(postulacion, total_items)


@router.patch("/{postulacion_id}/estado", response_model=PostulacionDetail)
def update_postulacion_estado(
    postulacion_id: int,
    payload: PostulacionStatusUpdate,
    _: Usuario = Depends(require_admin_role),
    service: PostulacionService = Depends(_get_service),
) -> PostulacionDetail:
    postulacion = service.update_status(postulacion_id, payload)
    total_items = service.repository.count_items(postulacion_id)
    return _to_detail(postulacion, total_items)
