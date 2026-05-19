from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_active_user, require_admin_role
from app.api.deps.db import get_db
from app.db.models.user import Usuario
from app.modules.convocatorias.repository import ConvocatoriaRepository
from app.modules.convocatorias.schemas.convocatoria import (
    ConvocatoriaActivaResponse,
    ConvocatoriaCreate,
    ConvocatoriaResponse,
    ConvocatoriaSummary,
    ConvocatoriaUpdate,
)
from app.modules.convocatorias.service import ConvocatoriaService

router = APIRouter()


def _get_service(db: object = Depends(get_db)) -> ConvocatoriaService:
    repo = ConvocatoriaRepository(db)  # type: ignore[arg-type]
    return ConvocatoriaService(repo, db=db)


@router.get("/activa", response_model=ConvocatoriaActivaResponse)
def get_convocatoria_activa(
    service: ConvocatoriaService = Depends(_get_service),
) -> ConvocatoriaActivaResponse:
    """Get the active convocatoria for aspirantes.
    
    Returns hay_convocatoria_activa=False with a message if none exists.
    """
    convocatorias = service.list_activas()
    if not convocatorias:
        return ConvocatoriaActivaResponse(
            hay_convocatoria_activa=False,
            convocatoria=None,
            mensaje="No hay convocatorias activas en este momento.",
        )
    conv = convocatorias[0]
    return ConvocatoriaActivaResponse(
        hay_convocatoria_activa=True,
        convocatoria=ConvocatoriaSummary(
            id_convocatoria=conv.id_convocatoria,
            titulo=conv.titulo,
            descripcion=conv.descripcion,
            fecha_inicio=conv.fecha_inicio,
            fecha_cierre=conv.fecha_cierre,
            activa=conv.activa,
        ),
    )


@router.get("", response_model=list[ConvocatoriaSummary])
def list_convocatorias(
    service: ConvocatoriaService = Depends(_get_service),
) -> list[ConvocatoriaSummary]:
    convocatorias = service.list_activas()
    return [
        ConvocatoriaSummary(
            id_convocatoria=c.id_convocatoria,
            titulo=c.titulo,
            descripcion=c.descripcion,
            fecha_inicio=c.fecha_inicio,
            fecha_cierre=c.fecha_cierre,
            activa=c.activa,
        )
        for c in convocatorias
    ]


@router.get("/todas", response_model=list[ConvocatoriaResponse])
def list_all_convocatorias(
    _: Usuario = Depends(require_admin_role),
    service: ConvocatoriaService = Depends(_get_service),
) -> list[ConvocatoriaResponse]:
    convocatorias = service.list_all()
    return [
        ConvocatoriaResponse(
            id_convocatoria=c.id_convocatoria,
            titulo=c.titulo,
            descripcion=c.descripcion,
            fecha_inicio=c.fecha_inicio,
            fecha_cierre=c.fecha_cierre,
            activa=c.activa,
            creado_por=c.creado_por,
            fecha_creacion=c.fecha_creacion,
            fecha_actualizacion=c.fecha_actualizacion,
        )
        for c in convocatorias
    ]


@router.get("/{convocatoria_id}", response_model=ConvocatoriaResponse)
def get_convocatoria(
    convocatoria_id: int,
    service: ConvocatoriaService = Depends(_get_service),
) -> ConvocatoriaResponse:
    convocatoria = service.get_by_id(convocatoria_id)
    return ConvocatoriaResponse(
        id_convocatoria=convocatoria.id_convocatoria,
        titulo=convocatoria.titulo,
        descripcion=convocatoria.descripcion,
        fecha_inicio=convocatoria.fecha_inicio,
        fecha_cierre=convocatoria.fecha_cierre,
        activa=convocatoria.activa,
        creado_por=convocatoria.creado_por,
        fecha_creacion=convocatoria.fecha_creacion,
        fecha_actualizacion=convocatoria.fecha_actualizacion,
    )


@router.post(
    "",
    response_model=ConvocatoriaResponse,
    status_code=201,
)
def create_convocatoria(
    payload: ConvocatoriaCreate,
    current_user: Usuario = Depends(require_admin_role),
    service: ConvocatoriaService = Depends(_get_service),
) -> ConvocatoriaResponse:
    convocatoria = service.create(payload, current_user.id_usuario)
    return ConvocatoriaResponse(
        id_convocatoria=convocatoria.id_convocatoria,
        titulo=convocatoria.titulo,
        descripcion=convocatoria.descripcion,
        fecha_inicio=convocatoria.fecha_inicio,
        fecha_cierre=convocatoria.fecha_cierre,
        activa=convocatoria.activa,
        creado_por=convocatoria.creado_por,
        fecha_creacion=convocatoria.fecha_creacion,
        fecha_actualizacion=convocatoria.fecha_actualizacion,
    )


@router.patch("/{convocatoria_id}", response_model=ConvocatoriaResponse)
def update_convocatoria(
    convocatoria_id: int,
    payload: ConvocatoriaUpdate,
    _: Usuario = Depends(require_admin_role),
    service: ConvocatoriaService = Depends(_get_service),
) -> ConvocatoriaResponse:
    convocatoria = service.update(convocatoria_id, payload)
    return ConvocatoriaResponse(
        id_convocatoria=convocatoria.id_convocatoria,
        titulo=convocatoria.titulo,
        descripcion=convocatoria.descripcion,
        fecha_inicio=convocatoria.fecha_inicio,
        fecha_cierre=convocatoria.fecha_cierre,
        activa=convocatoria.activa,
        creado_por=convocatoria.creado_por,
        fecha_creacion=convocatoria.fecha_creacion,
        fecha_actualizacion=convocatoria.fecha_actualizacion,
    )


@router.post("/{convocatoria_id}/toggle", response_model=ConvocatoriaResponse)
def toggle_convocatoria(
    convocatoria_id: int,
    _: Usuario = Depends(require_admin_role),
    service: ConvocatoriaService = Depends(_get_service),
) -> ConvocatoriaResponse:
    convocatoria = service.toggle_active(convocatoria_id)
    return ConvocatoriaResponse(
        id_convocatoria=convocatoria.id_convocatoria,
        titulo=convocatoria.titulo,
        descripcion=convocatoria.descripcion,
        fecha_inicio=convocatoria.fecha_inicio,
        fecha_cierre=convocatoria.fecha_cierre,
        activa=convocatoria.activa,
        creado_por=convocatoria.creado_por,
        fecha_creacion=convocatoria.fecha_creacion,
        fecha_actualizacion=convocatoria.fecha_actualizacion,
    )
