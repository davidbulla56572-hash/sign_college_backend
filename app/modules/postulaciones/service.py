from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.modules.postulaciones.repository import PostulacionRepository
from app.modules.postulaciones.schemas.postulacion import (
    ActiveDraftResponse,
    PostulacionApplyResponse,
    PostulacionCreate,
    PostulacionStatusUpdate,
)


class PostulacionService:
    def __init__(self, repository: PostulacionRepository) -> None:
        self.repository = repository

    # -- Aspirante operations --

    def create_for_user(
        self,
        user_id: int,
        data: PostulacionCreate,
    ) -> Postulacion:
        postulacion = self.repository.create(user_id, data)
        self.repository.commit()
        return postulacion

    def list_for_user(self, user_id: int) -> list[Postulacion]:
        return self.repository.list_by_user(user_id)

    def get_for_user(self, postulacion_id: int, user_id: int) -> Postulacion:
        postulacion = self.repository.get_for_user(postulacion_id, user_id)
        if postulacion is None:
            raise NotFoundError("Postulacion not found")
        return postulacion

    def submit(self, postulacion_id: int, user_id: int) -> Postulacion:
        postulacion = self.get_for_user(postulacion_id, user_id)
        submitted = self.repository.submit(postulacion)
        self.repository.commit()
        return submitted

    def get_or_create_active_draft(self, user_id: int) -> ActiveDraftResponse:
        """Get or create draft for the active convocatoria."""
        postulacion, ya_existia = self.repository.get_or_create_draft_for_active_convocatoria(user_id)
        self.repository.commit()
        return ActiveDraftResponse(
            id_postulacion=postulacion.id_postulacion,
            id_convocatoria=postulacion.id_convocatoria,
            estado=postulacion.estado,
            ya_existia=ya_existia,
        )

    def apply(self, postulacion_id: int, user_id: int) -> PostulacionApplyResponse:
        """Apply/send the postulacion."""
        postulacion = self.get_for_user(postulacion_id, user_id)
        submitted = self.repository.submit(postulacion)
        self.repository.commit()
        return PostulacionApplyResponse(
            id_postulacion=submitted.id_postulacion,
            estado=submitted.estado,
            puntaje_total=submitted.puntaje_total,
            mensaje="La postulacion fue enviada correctamente.",
        )

    # -- Admin operations --

    def list_all(
        self,
        estado: PostulacionEstado | None = None,
    ) -> list[Postulacion]:
        return self.repository.list_all(estado)

    def get_by_id(self, postulacion_id: int) -> Postulacion:
        postulacion = self.repository.get_by_id(postulacion_id)
        if postulacion is None:
            raise NotFoundError("Postulacion not found")
        return postulacion

    def update_status(
        self,
        postulacion_id: int,
        data: PostulacionStatusUpdate,
    ) -> Postulacion:
        postulacion = self.get_by_id(postulacion_id)
        updated = self.repository.update_status(postulacion, data)
        self.repository.commit()
        return updated

    def evaluate(
        self,
        postulacion_id: int,
        puntaje: float,
    ) -> Postulacion:
        postulacion = self.get_by_id(postulacion_id)
        postulacion.puntaje_total = puntaje
        if postulacion.estado != PostulacionEstado.RECHAZADA:
            postulacion.estado = PostulacionEstado.EVALUADA
        postulacion.fecha_evaluacion = None  # will be set by update_status
        updated = self.repository.update_status(
            postulacion,
            PostulacionStatusUpdate(estado=postulacion.estado),
        )
        self.repository.commit()
        return updated
