from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.models.hoja_vida import TipoItemHojaVida
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.modules.postulaciones.repository import PostulacionRepository
from app.modules.postulaciones.schemas.postulacion import (
    ActiveDraftResponse,
    PostulacionApplyResponse,
    PostulacionCreate,
    PostulacionFlowSummary,
    PostulacionResumenItems,
    PostulacionSummaryConvocatoria,
    PostulacionSummaryDatosPersonales,
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
        summary = self.get_summary_for_user(postulacion_id, user_id)
        if not summary.lista_para_aplicar:
            from app.core.exceptions import ConflictError

            raise ConflictError(
                "La postulacion no esta lista para enviarse. Revisa tu hoja de vida y el resumen."
            )
        postulacion = self.get_for_user(postulacion_id, user_id)
        submitted = self.repository.submit(postulacion)
        self.repository.commit()
        return PostulacionApplyResponse(
            id_postulacion=submitted.id_postulacion,
            estado=submitted.estado,
            puntaje_total=submitted.puntaje_total,
            mensaje="La postulacion fue enviada correctamente.",
        )

    def get_summary_for_user(
        self,
        postulacion_id: int,
        user_id: int,
    ) -> PostulacionFlowSummary:
        postulacion = self.get_for_user(postulacion_id, user_id)
        convocatoria = postulacion.convocatoria
        if convocatoria is None:
            raise NotFoundError("Convocatoria not found")

        counts = self.repository.count_items_by_tipo(postulacion_id)
        resumen_items = PostulacionResumenItems(
            formacion=counts.get(TipoItemHojaVida.FORMACION, 0),
            experiencia=counts.get(TipoItemHojaVida.EXPERIENCIA, 0),
            produccion=counts.get(TipoItemHojaVida.PRODUCCION, 0),
            ponencia=counts.get(TipoItemHojaVida.PONENCIA, 0),
            investigacion=counts.get(TipoItemHojaVida.INVESTIGACION, 0),
        )
        total_items = sum(counts.values())
        tiene_cv_cargado = bool(postulacion.url_cv_original)
        lista_para_aplicar = (
            postulacion.estado == PostulacionEstado.BORRADOR
            and tiene_cv_cargado
            and bool(postulacion.usuario)
            and bool(postulacion.usuario.nombre.strip())
            and bool(postulacion.usuario.apellido.strip())
            and total_items > 0
        )

        return PostulacionFlowSummary(
            id_postulacion=postulacion.id_postulacion,
            estado=postulacion.estado,
            convocatoria=PostulacionSummaryConvocatoria(
                id_convocatoria=convocatoria.id_convocatoria,
                titulo=convocatoria.titulo,
            ),
            datos_personales=PostulacionSummaryDatosPersonales(
                nombre=postulacion.usuario.nombre if postulacion.usuario else "",
                apellido=postulacion.usuario.apellido if postulacion.usuario else "",
                email=postulacion.usuario.email if postulacion.usuario else None,
            ),
            resumen_items=resumen_items,
            lista_para_aplicar=lista_para_aplicar,
            total_items=total_items,
            tiene_cv_cargado=tiene_cv_cargado,
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
