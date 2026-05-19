from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.convocatoria import Convocatoria
from app.db.models.hoja_vida import ItemHojaVida
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.modules.postulaciones.schemas.postulacion import (
    PostulacionCreate,
    PostulacionStatusUpdate,
)


class PostulacionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, postulacion_id: int) -> Postulacion | None:
        statement = (
            select(Postulacion)
            .where(Postulacion.id_postulacion == postulacion_id)
            .options(
                joinedload(Postulacion.convocatoria),
                joinedload(Postulacion.usuario),
            )
        )
        return self.db.scalar(statement)

    def get_for_user(
        self,
        postulacion_id: int,
        user_id: int,
    ) -> Postulacion | None:
        statement = (
            select(Postulacion)
            .where(
                Postulacion.id_postulacion == postulacion_id,
                Postulacion.id_usuario == user_id,
            )
            .options(joinedload(Postulacion.convocatoria))
        )
        return self.db.scalar(statement)

    def list_by_user(self, user_id: int) -> list[Postulacion]:
        statement = (
            select(Postulacion)
            .where(Postulacion.id_usuario == user_id)
            .options(joinedload(Postulacion.convocatoria))
            .order_by(Postulacion.fecha_creacion.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_all(
        self,
        estado: PostulacionEstado | None = None,
    ) -> list[Postulacion]:
        statement = (
            select(Postulacion)
            .options(
                joinedload(Postulacion.usuario),
                joinedload(Postulacion.convocatoria),
            )
            .order_by(Postulacion.fecha_creacion.desc())
        )
        if estado is not None:
            statement = statement.where(Postulacion.estado == estado)
        return list(self.db.scalars(statement).all())

    def count_items(self, postulacion_id: int) -> int:
        statement = (
            select(func.count(ItemHojaVida.id_item))
            .where(ItemHojaVida.id_postulacion == postulacion_id)
        )
        return self.db.scalar(statement) or 0

    def create(
        self,
        user_id: int,
        data: PostulacionCreate,
    ) -> Postulacion:
        # Verify convocatoria exists
        conv_stmt = select(Convocatoria).where(
            Convocatoria.id_convocatoria == data.id_convocatoria
        )
        convocatoria = self.db.scalar(conv_stmt)
        if convocatoria is None:
            raise NotFoundError("Convocatoria not found")

        # Check for existing postulacion
        existing = self.db.scalar(
            select(Postulacion).where(
                Postulacion.id_usuario == user_id,
                Postulacion.id_convocatoria == data.id_convocatoria,
            )
        )
        if existing is not None:
            raise ConflictError(
                "Ya existe una postulacion para esta convocatoria"
            )

        postulacion = Postulacion(
            id_usuario=user_id,
            id_convocatoria=data.id_convocatoria,
            estado=PostulacionEstado.BORRADOR,
        )
        self.db.add(postulacion)
        self.db.flush()
        return postulacion

    def submit(self, postulacion: Postulacion) -> Postulacion:
        if postulacion.estado != PostulacionEstado.BORRADOR:
            raise ConflictError(
                "Solo se pueden enviar postulaciones en estado BORRADOR"
            )
        postulacion.estado = PostulacionEstado.ENVIADA
        postulacion.fecha_envio = datetime.now(UTC)
        self.db.flush()
        return postulacion

    def update_status(
        self,
        postulacion: Postulacion,
        data: PostulacionStatusUpdate,
    ) -> Postulacion:
        postulacion.estado = data.estado
        if data.observaciones_admin is not None:
            postulacion.observaciones_admin = data.observaciones_admin
        if data.estado == PostulacionEstado.EVALUADA:
            postulacion.fecha_evaluacion = datetime.now(UTC)
        self.db.flush()
        return postulacion

    def commit(self) -> None:
        self.db.commit()

    def get_or_create_draft_for_active_convocatoria(
        self, user_id: int
    ) -> tuple[Postulacion, bool]:
        """Get or create a draft postulacion for the active convocatoria.
        
        Returns (postulacion, ya_existia).
        """
        # Find active convocatoria
        conv_stmt = (
            select(Convocatoria)
            .where(Convocatoria.activa.is_(True))
            .limit(1)
        )
        convocatoria = self.db.scalar(conv_stmt)
        if convocatoria is None:
            raise NotFoundError("No hay convocatorias activas disponibles")

        # Check for existing draft/active postulacion
        existing = self.db.scalar(
            select(Postulacion).where(
                Postulacion.id_usuario == user_id,
                Postulacion.id_convocatoria == convocatoria.id_convocatoria,
                Postulacion.estado.in_([
                    PostulacionEstado.BORRADOR,
                    PostulacionEstado.ENVIADA,
                ]),
            )
        )
        if existing is not None:
            return existing, True

        # Create new draft
        postulacion = Postulacion(
            id_usuario=user_id,
            id_convocatoria=convocatoria.id_convocatoria,
            estado=PostulacionEstado.BORRADOR,
        )
        self.db.add(postulacion)
        self.db.flush()
        return postulacion, False
