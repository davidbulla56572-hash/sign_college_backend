from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.models.hoja_vida import ItemHojaVida, TipoItemHojaVida
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.db.models.regla_evaluacion import ReglaEvaluacion
from app.modules.evaluation.schemas.evaluation import (
    DetalleSeccion,
    EvaluationResult,
    ItemEvaluadoDetalle,
)


class EvaluacionError(AppError):
    status_code = 400
    code = "evaluacion_error"


class EvaluationService:
    """Calcula puntajes aplicando reglas de evaluacion a items de hoja de vida.

    Persiste puntaje_asignado por item, actualiza puntaje_total,
    fecha_evaluacion y estado de la postulacion.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def evaluate_postulacion(
        self, postulacion_id: int
    ) -> EvaluationResult:
        """Evalua una postulacion SIN persistir cambios.
        Retorna el resultado del calculo para revision.
        """
        postulacion = self._get_postulacion(postulacion_id)
        reglas = self._get_reglas(postulacion.id_convocatoria)
        items = self._get_items(postulacion_id)

        if not items:
            raise EvaluacionError(
                "La postulacion no tiene items de hoja de vida para evaluar"
            )

        if not reglas:
            raise EvaluacionError(
                "La convocatoria no tiene reglas de evaluacion configuradas"
            )

        # Group items by tipo_item
        items_by_tipo: dict[TipoItemHojaVida, list[ItemHojaVida]] = {}
        for item in items:
            items_by_tipo.setdefault(item.tipo_item, []).append(item)

        desglose: list[DetalleSeccion] = []
        item_detalles: list[ItemEvaluadoDetalle] = []
        puntaje_total = 0.0
        total_items_evaluated = 0

        for tipo_item, regla in reglas.items():
            section_items = items_by_tipo.get(tipo_item, [])
            if not section_items:
                continue

            # Calculate quantity: use cantidad field if set, else count as 1 per item
            cantidad = sum(
                item.cantidad if item.cantidad and item.cantidad > 0 else 1
                for item in section_items
            )

            puntaje_bruto = cantidad * regla.puntaje_unitario

            # Apply cap if maximo_acumulable is set
            if regla.maximo_acumulable is not None:
                puntaje_final = min(puntaje_bruto, regla.maximo_acumulable)
            else:
                puntaje_final = puntaje_bruto

            # Distribute score proportionally among items
            puntaje_total += puntaje_final
            total_items_evaluated += len(section_items)

            for item in section_items:
                item_cantidad = (
                    item.cantidad if item.cantidad and item.cantidad > 0 else 1
                )
                if cantidad > 0:
                    item_puntaje = round(
                        (item_cantidad / cantidad) * puntaje_final, 2
                    )
                else:
                    item_puntaje = 0.0

                item_detalles.append(
                    ItemEvaluadoDetalle(
                        id_item=item.id_item,
                        tipo_item=item.tipo_item,
                        descripcion=item.descripcion,
                        puntaje_asignado=item_puntaje,
                    )
                )

            desglose.append(
                DetalleSeccion(
                    tipo_item=tipo_item,
                    descripcion_regla=regla.descripcion_regla,
                    cantidad_items=cantidad,
                    puntaje_unitario=regla.puntaje_unitario,
                    puntaje_bruto=round(puntaje_bruto, 2),
                    maximo_acumulable=regla.maximo_acumulable,
                    puntaje_final=round(puntaje_final, 2),
                )
            )

        # Report items without rules (items whose tipo_item has no matching rule)
        items_sin_regla = [
            item
            for item in items
            if item.tipo_item not in reglas
        ]
        if items_sin_regla:
            raise EvaluacionError(
                f"Hay {len(items_sin_regla)} items sin regla de evaluacion "
                f"asociada en esta convocatoria"
            )

        return EvaluationResult(
            postulacion_id=postulacion_id,
            puntaje_total=round(puntaje_total, 2),
            desglose=desglose,
            item_detalles=item_detalles,
            reglas_aplicadas=len(desglose),
            items_evaluados=total_items_evaluated,
        )

    def apply_evaluation(self, postulacion_id: int) -> EvaluationResult:
        """Evalua, persiste puntajes por item, actualiza estado y fecha."""
        from datetime import UTC, datetime

        result = self.evaluate_postulacion(postulacion_id)

        postulacion = self._get_postulacion(postulacion_id)

        # Persist puntaje_asignado on each item
        for item_det in result.item_detalles:
            item_stmt = select(ItemHojaVida).where(
                ItemHojaVida.id_item == item_det.id_item
            )
            item = self.db.scalar(item_stmt)
            if item is not None:
                item.puntaje_asignado = item_det.puntaje_asignado
                item.validado = True

        # Update postulacion
        postulacion.puntaje_total = result.puntaje_total
        postulacion.fecha_evaluacion = datetime.now(UTC)

        # State transition: ENVIADA -> EVALUADA (or keep EN_EVALUACION)
        if postulacion.estado == PostulacionEstado.ENVIADA:
            postulacion.estado = PostulacionEstado.EVALUADA
        elif postulacion.estado == PostulacionEstado.EN_EVALUACION:
            postulacion.estado = PostulacionEstado.EVALUADA
        elif postulacion.estado == PostulacionEstado.BORRADOR:
            # Auto-submit then evaluate
            postulacion.fecha_envio = datetime.now(UTC)
            postulacion.estado = PostulacionEstado.EVALUADA

        self.db.commit()
        return result

    def evaluate_convocatoria_ranking(
        self,
        convocatoria_id: int,
    ) -> dict:
        """Returns ranking of all evaluated postulaciones in a convocatoria.

        Returns format: {id_convocatoria, titulo_convocatoria, items: [...], total: N}
        """
        from app.db.models.convocatoria import Convocatoria

        conv_stmt = select(Convocatoria).where(
            Convocatoria.id_convocatoria == convocatoria_id
        )
        convocatoria = self.db.scalar(conv_stmt)
        if convocatoria is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError("Convocatoria not found")

        statement = (
            select(Postulacion)
            .where(Postulacion.id_convocatoria == convocatoria_id)
            .order_by(Postulacion.puntaje_total.desc().nullslast())
        )
        postulaciones = list(self.db.scalars(statement).all())

        ranking_items = []
        for p in postulaciones:
            ranking_items.append(
                {
                    "id_postulacion": p.id_postulacion,
                    "id_usuario": p.id_usuario,
                    "aspirante": f"{p.usuario.nombre or ''} {p.usuario.apellido or ''}".strip(),
                    "cedula": p.usuario.cedula if p.usuario else "",
                    "estado": p.estado.value,
                    "puntaje_total": p.puntaje_total,
                    "convocatoria": convocatoria.titulo,
                    "fecha_evaluacion": p.fecha_evaluacion,
                }
            )

        return {
            "id_convocatoria": convocatoria_id,
            "titulo_convocatoria": convocatoria.titulo,
            "items": ranking_items,
            "total": len(ranking_items),
        }

    def get_resultado_detalle(
        self, postulacion_id: int
    ) -> dict:
        """Returns detailed result for a postulacion."""
        postulacion = self._get_postulacion(postulacion_id)
        items = self._get_items(postulacion_id)

        return {
            "id_postulacion": postulacion.id_postulacion,
            "estado": postulacion.estado.value,
            "puntaje_total": postulacion.puntaje_total,
            "fecha_evaluacion": postulacion.fecha_evaluacion,
            "convocatoria": {
                "id_convocatoria": postulacion.id_convocatoria,
                "titulo": postulacion.convocatoria.titulo
                if postulacion.convocatoria
                else "",
            },
            "detalle": [
                {
                    "id_item": item.id_item,
                    "tipo_item": item.tipo_item.value,
                    "descripcion": item.descripcion,
                    "puntaje_asignado": item.puntaje_asignado or 0.0,
                }
                for item in items
            ],
        }

    def _get_postulacion(self, postulacion_id: int) -> Postulacion:
        statement = select(Postulacion).where(
            Postulacion.id_postulacion == postulacion_id
        )
        postulacion = self.db.scalar(statement)
        if postulacion is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError(f"Postulacion {postulacion_id} not found")
        return postulacion

    def _get_reglas(
        self, convocatoria_id: int
    ) -> dict[TipoItemHojaVida, ReglaEvaluacion]:
        statement = select(ReglaEvaluacion).where(
            ReglaEvaluacion.id_convocatoria == convocatoria_id
        )
        reglas = self.db.scalars(statement).all()
        return {r.tipo_item: r for r in reglas}

    def _get_items(self, postulacion_id: int) -> list[ItemHojaVida]:
        statement = select(ItemHojaVida).where(
            ItemHojaVida.id_postulacion == postulacion_id
        )
        return list(self.db.scalars(statement).all())
