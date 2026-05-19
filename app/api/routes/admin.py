from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.api.deps.auth import require_admin_role
from app.api.deps.db import get_db
from app.db.models.hoja_vida import SoporteItem
from app.db.models.postulacion import Postulacion
from app.db.models.user import UserRole, Usuario
from app.modules.admin.schemas.admin import (
    AdminAspirantDetail,
    AdminAspirantSummary,
    AdminPostulacionDetalle,
    AdminSoporteItem,
)

router = APIRouter()


def _get_db(db: Session = Depends(get_db)) -> Session:
    return db


def _format_dt(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


# -- Aspirants listing --

@router.get("/aspirantes", response_model=list[AdminAspirantSummary])
def list_aspirantes(
    db: Session = Depends(_get_db),
    _: Usuario = Depends(require_admin_role),
) -> list[AdminAspirantSummary]:
    statement = (
        select(Usuario)
        .where(Usuario.rol == UserRole.ASPIRANTE)
        .order_by(Usuario.fecha_registro.desc())
    )
    users = list(db.scalars(statement).all())
    return [
        AdminAspirantSummary(
            id_usuario=u.id_usuario,
            nombre=u.nombre,
            apellido=u.apellido,
            cedula=u.cedula,
            email=u.email,
            telefono=u.telefono,
            municipio=u.municipio,
            departamento=u.departamento,
            fecha_registro=u.fecha_registro,
        )
        for u in users
    ]


@router.get("/aspirantes/{user_id}", response_model=AdminAspirantDetail)
def get_aspirant_detail(
    user_id: int,
    db: Session = Depends(_get_db),
    _: Usuario = Depends(require_admin_role),
) -> AdminAspirantDetail:
    statement = select(Usuario).where(Usuario.id_usuario == user_id)
    user = db.scalar(statement)
    if user is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Aspirante not found")

    post_stmt = (
        select(Postulacion)
        .where(Postulacion.id_usuario == user_id)
        .options(joinedload(Postulacion.convocatoria))
        .order_by(Postulacion.fecha_creacion.desc())
    )
    postulaciones = list(db.scalars(post_stmt).all())

    return AdminAspirantDetail(
        id_usuario=user.id_usuario,
        nombre=user.nombre,
        apellido=user.apellido,
        cedula=user.cedula,
        email=user.email,
        telefono=user.telefono,
        municipio=user.municipio,
        departamento=user.departamento,
        pais=user.pais,
        postulaciones=[
            {
                "id_postulacion": p.id_postulacion,
                "titulo_convocatoria": p.convocatoria.titulo
                if p.convocatoria
                else "",
                "estado": p.estado.value,
                "puntaje_total": p.puntaje_total,
                "fecha_envio": _format_dt(p.fecha_envio),
            }
            for p in postulaciones
        ],
    )


# -- Postulacion detail with soportes --

@router.get(
    "/postulaciones/{postulacion_id}/detalle",
    response_model=AdminPostulacionDetalle,
)
def get_postulacion_detalle(
    postulacion_id: int,
    db: Session = Depends(_get_db),
    _: Usuario = Depends(require_admin_role),
) -> AdminPostulacionDetalle:
    from app.db.models.hoja_vida import ItemHojaVida

    post_stmt = (
        select(Postulacion)
        .where(Postulacion.id_postulacion == postulacion_id)
        .options(
            joinedload(Postulacion.usuario),
            joinedload(Postulacion.convocatoria),
        )
    )
    postulacion = db.scalar(post_stmt)
    if postulacion is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Postulacion not found")

    # Get items with soportes
    items_stmt = (
        select(ItemHojaVida)
        .where(ItemHojaVida.id_postulacion == postulacion_id)
    )
    items = list(db.scalars(items_stmt).all())

    soportes: list[AdminSoporteItem] = []
    for item in items:
        sop_stmt = (
            select(SoporteItem)
            .where(SoporteItem.id_item == item.id_item)
        )
        item_soportes = list(db.scalars(sop_stmt).all())
        soportes.extend(
            AdminSoporteItem(
                id_soporte=s.id_soporte,
                id_item=s.id_item,
                nombre_archivo=s.nombre_archivo,
                url_archivo=s.url_archivo,
                tipo_archivo=s.tipo_archivo,
                tamanio_bytes=s.tamanio_bytes,
                fecha_carga=s.fecha_carga,
            )
            for s in item_soportes
        )

    return AdminPostulacionDetalle(
        id_postulacion=postulacion.id_postulacion,
        id_usuario=postulacion.id_usuario,
        aspirante_nombre=postulacion.usuario.nombre
        if postulacion.usuario
        else "",
        aspirante_apellido=postulacion.usuario.apellido
        if postulacion.usuario
        else "",
        aspirante_cedula=postulacion.usuario.cedula
        if postulacion.usuario
        else "",
        titulo_convocatoria=postulacion.convocatoria.titulo
        if postulacion.convocatoria
        else "",
        estado=postulacion.estado,
        puntaje_total=postulacion.puntaje_total,
        url_cv_original=postulacion.url_cv_original,
        observaciones_admin=postulacion.observaciones_admin,
        fecha_envio=postulacion.fecha_envio,
        fecha_evaluacion=postulacion.fecha_evaluacion,
        total_items=len(items),
        soportes=soportes,
    )
