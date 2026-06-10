from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.models.hoja_vida import ItemHojaVida, SoporteItem
from app.db.models.postulacion import Postulacion
from app.db.models.regla_evaluacion import ReglaEvaluacion
from app.modules.admin.schemas.admin import (
    AdminItemDetalle,
    AdminPostulacionDetalleCompleto,
    AdminSoporteItemSimple,
    EvaluationTraceItem,
    EvaluationTraceResponse,
    ItemValidationResponse,
    ObservacionesResponse,
)


class AdminPostulacionReviewService:
    """Admin-facing review: detalle completo, validacion de items, observaciones, trazabilidad."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # -- Detalle completo con items y soportes anidados --

    def get_postulacion_detalle_completo(
        self, postulacion_id: int
    ) -> AdminPostulacionDetalleCompleto:
        postulacion = self._get_postulacion(postulacion_id)
        items = self._get_items(postulacion_id)

        items_detalle: list[AdminItemDetalle] = []
        for item in items:
            soportes = self._get_soportes_for_item(item.id_item)
            items_detalle.append(
                AdminItemDetalle(
                    id_item=item.id_item,
                    tipo_item=item.tipo_item,
                    descripcion=item.descripcion,
                    institucion=item.institucion,
                    fecha_inicio=item.fecha_inicio.isoformat() if item.fecha_inicio else None,
                    fecha_fin=item.fecha_fin.isoformat() if item.fecha_fin else None,
                    cantidad=item.cantidad,
                    puntaje_asignado=float(item.puntaje_asignado) if item.puntaje_asignado else None,
                    validado=item.validado,
                    soportes=[
                        AdminSoporteItemSimple(
                            id_soporte=s.id_soporte,
                            nombre_archivo=s.nombre_archivo,
                            url_archivo=s.url_archivo,
                            tipo_archivo=s.tipo_archivo,
                            tamanio_bytes=s.tamanio_bytes,
                            fecha_carga=s.fecha_carga,
                        )
                        for s in soportes
                    ],
                )
            )

        return AdminPostulacionDetalleCompleto(
            id_postulacion=postulacion.id_postulacion,
            id_usuario=postulacion.id_usuario,
            aspirante_nombre=postulacion.usuario.nombre if postulacion.usuario else "",
            aspirante_apellido=postulacion.usuario.apellido if postulacion.usuario else "",
            aspirante_cedula=postulacion.usuario.cedula if postulacion.usuario else "",
            aspirante_email=postulacion.usuario.email if postulacion.usuario else "",
            id_convocatoria=postulacion.id_convocatoria,
            titulo_convocatoria=postulacion.convocatoria.titulo if postulacion.convocatoria else "",
            estado=postulacion.estado,
            puntaje_total=float(postulacion.puntaje_total) if postulacion.puntaje_total else None,
            fecha_envio=postulacion.fecha_envio,
            fecha_evaluacion=postulacion.fecha_evaluacion,
            observaciones_admin=postulacion.observaciones_admin,
            items=items_detalle,
        )

    # -- Validacion de item --

    def validate_item(
        self, item_id: int, validado: bool
    ) -> ItemValidationResponse:
        item = self._get_item(item_id)
        item.validado = validado
        self.db.commit()
        return ItemValidationResponse(
            id_item=item.id_item,
            validado=item.validado,
            tipo_item=item.tipo_item,
            descripcion=item.descripcion,
        )

    def toggle_item_validation(self, item_id: int) -> ItemValidationResponse:
        item = self._get_item(item_id)
        item.validado = not item.validado
        self.db.commit()
        return ItemValidationResponse(
            id_item=item.id_item,
            validado=item.validado,
            tipo_item=item.tipo_item,
            descripcion=item.descripcion,
        )

    # -- Observaciones administrativas --

    def save_observaciones(
        self, postulacion_id: int, observaciones: str | None
    ) -> ObservacionesResponse:
        postulacion = self._get_postulacion(postulacion_id)
        postulacion.observaciones_admin = observaciones
        self.db.commit()
        return ObservacionesResponse(
            id_postulacion=postulacion.id_postulacion,
            observaciones_admin=postulacion.observaciones_admin,
        )

    # -- Soportes de un item (admin context) --

    def get_item_soportes(self, item_id: int) -> list[AdminSoporteItemSimple]:
        self._get_item(item_id)  # ensure item exists
        soportes = self._get_soportes_for_item(item_id)
        return [
            AdminSoporteItemSimple(
                id_soporte=s.id_soporte,
                nombre_archivo=s.nombre_archivo,
                url_archivo=s.url_archivo,
                tipo_archivo=s.tipo_archivo,
                tamanio_bytes=s.tamanio_bytes,
                fecha_carga=s.fecha_carga,
            )
            for s in soportes
        ]

    # -- Trazabilidad de evaluacion (Fase 14: delega a EvaluationService) --

    def get_evaluation_trace(self, postulacion_id: int) -> EvaluationTraceResponse:
        """Delegates to EvaluationService for consistent trace (14.17)."""
        from app.modules.evaluation.service import EvaluationService

        eval_service = EvaluationService(self.db)
        return eval_service.get_evaluation_trace(postulacion_id)

    # -- Recalcular evaluacion (Fase 14) --

    def recalculate_evaluation(self, postulacion_id: int) -> EvaluationTraceResponse:
        """Recalcula la evaluacion y retorna la nueva trazabilidad."""
        from app.modules.evaluation.service import EvaluationService

        eval_service = EvaluationService(self.db)
        result = eval_service.recalculate_evaluation(postulacion_id)
        return eval_service.get_evaluation_trace(postulacion_id)

    # -- Private helpers --

    def _get_postulacion(self, postulacion_id: int) -> Postulacion:
        from sqlalchemy.orm import joinedload

        statement = (
            select(Postulacion)
            .where(Postulacion.id_postulacion == postulacion_id)
            .options(
                joinedload(Postulacion.usuario),
                joinedload(Postulacion.convocatoria),
            )
        )
        postulacion = self.db.scalar(statement)
        if postulacion is None:
            raise NotFoundError("Postulacion no encontrada")
        return postulacion

    def _get_item(self, item_id: int) -> ItemHojaVida:
        statement = select(ItemHojaVida).where(ItemHojaVida.id_item == item_id)
        item = self.db.scalar(statement)
        if item is None:
            raise NotFoundError("Item de hoja de vida no encontrado")
        return item

    def _get_items(self, postulacion_id: int) -> list[ItemHojaVida]:
        statement = (
            select(ItemHojaVida)
            .where(ItemHojaVida.id_postulacion == postulacion_id)
            .order_by(ItemHojaVida.tipo_item, ItemHojaVida.id_item)
        )
        return list(self.db.scalars(statement).all())

    def _get_soportes_for_item(self, item_id: int) -> list[SoporteItem]:
        statement = (
            select(SoporteItem)
            .where(SoporteItem.id_item == item_id)
            .order_by(SoporteItem.fecha_carga.desc())
        )
        return list(self.db.scalars(statement).all())

    def _get_reglas(self, convocatoria_id: int) -> dict:
        statement = select(ReglaEvaluacion).where(
            ReglaEvaluacion.id_convocatoria == convocatoria_id
        )
        reglas = self.db.scalars(statement).all()
        return {r.tipo_item: r for r in reglas}
