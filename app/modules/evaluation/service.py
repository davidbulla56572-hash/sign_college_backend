from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFoundError
from app.db.models.convocatoria import Convocatoria
from app.db.models.hoja_vida import ItemHojaVida, TipoItemHojaVida
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.db.models.regla_evaluacion import ReglaEvaluacion
from app.modules.evaluation.schemas.evaluation import (
    DetalleSeccion,
    EvaluationResult,
    EvaluationTraceItem,
    EvaluationTraceResponse,
    ItemEvaluadoDetalle,
    ReglaAplicadaInfo,
)


class EvaluacionError(AppError):
    status_code = 400
    code = "evaluacion_error"


class EvaluationService:
    """Calcula puntajes aplicando reglas de evaluacion a items de hoja de vida.

    Persiste puntaje_asignado por item, actualiza puntaje_total,
    fecha_evaluacion y estado de la postulacion.

    Fase 14 refinements:
    - Items sin regla se asignan 0 pts con advertencia (no error)
    - Trazabilidad incluye regla_aplicada
    - Puntaje total se recalcula consistentemente desde items
    - Evaluacion es idempotente / re-ejecutable
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def evaluate_postulacion(
        self, postulacion_id: int
    ) -> EvaluationResult:
        """Evalua una postulacion SIN persistir cambios.
        Retorna el resultado del calculo para revision.

        Items sin regla asociada reciben 0 pts y se reportan como advertencia.
        """
        postulacion = self._get_postulacion(postulacion_id)
        reglas = self._get_reglas(postulacion.id_convocatoria)
        items = self._get_items(postulacion_id)

        if not items:
            raise EvaluacionError(
                "La postulacion no tiene items de hoja de vida para evaluar"
            )

        # Group items by tipo_item
        items_by_tipo: dict[TipoItemHojaVida, list[ItemHojaVida]] = {}
        for item in items:
            items_by_tipo.setdefault(item.tipo_item, []).append(item)

        desglose: list[DetalleSeccion] = []
        item_detalles: list[ItemEvaluadoDetalle] = []
        puntaje_total = 0.0
        total_items_evaluated = 0
        items_sin_regla = 0
        advertencias: list[str] = []

        for tipo_item, regla in reglas.items():
            section_items = items_by_tipo.get(tipo_item, [])
            if not section_items:
                continue

            # Calculate quantity: use cantidad field if set, else count as 1 per item
            cantidad = sum(
                item.cantidad if item.cantidad and item.cantidad > 0 else 1
                for item in section_items
            )

            # Convert Decimal to float for consistent arithmetic (Numeric columns)
            puntaje_unitario = float(regla.puntaje_unitario)
            maximo_acumulable = (
                float(regla.maximo_acumulable) if regla.maximo_acumulable is not None else None
            )

            puntaje_bruto = cantidad * puntaje_unitario

            # Apply cap if maximo_acumulable is set
            if maximo_acumulable is not None:
                puntaje_final = min(puntaje_bruto, maximo_acumulable)
            else:
                puntaje_final = puntaje_bruto

            # Safety: never allow negative scores (14.18)
            puntaje_final = max(0.0, puntaje_final)

            puntaje_total += puntaje_final
            total_items_evaluated += len(section_items)

            # Distribute score proportionally among items
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
                    puntaje_unitario=round(puntaje_unitario, 2),
                    puntaje_bruto=round(puntaje_bruto, 2),
                    maximo_acumulable=maximo_acumulable,
                    puntaje_final=round(puntaje_final, 2),
                )
            )

        # Handle items without rules: assign 0 pts with warning (14.13, 14.14)
        items_sin_regla_list = [
            item
            for item in items
            if item.tipo_item not in reglas
        ]
        if items_sin_regla_list:
            items_sin_regla = len(items_sin_regla_list)
            for item in items_sin_regla_list:
                item_detalles.append(
                    ItemEvaluadoDetalle(
                        id_item=item.id_item,
                        tipo_item=item.tipo_item,
                        descripcion=item.descripcion,
                        puntaje_asignado=0.0,
                    )
                )
                advertencias.append(
                    f"Item #{item.id_item} ({item.tipo_item.value}): sin regla de evaluacion, asignado 0 pts"
                )

        return EvaluationResult(
            postulacion_id=postulacion_id,
            id_convocatoria=postulacion.id_convocatoria,
            puntaje_total=round(puntaje_total, 2),
            desglose=desglose,
            item_detalles=item_detalles,
            reglas_aplicadas=len(desglose),
            items_evaluados=total_items_evaluated,
            items_sin_regla=items_sin_regla,
            advertencias=advertencias,
        )

    def apply_evaluation(self, postulacion_id: int) -> EvaluationResult:
        """Evalua, persiste puntajes por item, actualiza estado y fecha.
        Idempotente: puede re-ejecutarse sobre postulaciones ya evaluadas.
        """
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
                # Set validado=True only if the item had a rule applied
                if item_det.puntaje_asignado > 0:
                    item.validado = True

        # Update postulacion with consistent total (14.18)
        postulacion.puntaje_total = result.puntaje_total
        postulacion.fecha_evaluacion = datetime.now(UTC)

        # State transitions (14.19)
        if postulacion.estado == PostulacionEstado.ENVIADA:
            postulacion.estado = PostulacionEstado.EN_EVALUACION
        elif postulacion.estado == PostulacionEstado.BORRADOR:
            postulacion.fecha_envio = datetime.now(UTC)
            postulacion.estado = PostulacionEstado.EN_EVALUACION

        # Always set to EVALUADA after evaluation completes
        if postulacion.estado in (PostulacionEstado.EN_EVALUACION, PostulacionEstado.EVALUADA):
            postulacion.estado = PostulacionEstado.EVALUADA

        self.db.commit()
        return result

    def recalculate_evaluation(self, postulacion_id: int) -> EvaluationResult:
        """Recalcula la evaluacion de una postulacion existente.

        Re-ejecuta el calculo desde cero con las reglas e items actuales.
        Persiste los nuevos valores. Permite actualizar resultados cuando
        cambian reglas o items.
        """
        postulacion = self._get_postulacion(postulacion_id)

        # Reset existing item scores before recalculating
        for item in self._get_items(postulacion_id):
            item.puntaje_asignado = None
            item.validado = False

        # Reset postulacion totals
        postulacion.puntaje_total = None

        # Re-evaluate
        result = self.apply_evaluation(postulacion_id)
        return result

    def evaluate_convocatoria_ranking(
        self,
        convocatoria_id: int,
    ) -> dict:
        """Returns ranking of all evaluated postulaciones in a convocatoria.

        Returns format: {id_convocatoria, titulo_convocatoria, items: [...], total: N}
        """
        conv_stmt = select(Convocatoria).where(
            Convocatoria.id_convocatoria == convocatoria_id
        )
        convocatoria = self.db.scalar(conv_stmt)
        if convocatoria is None:
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

    def get_evaluation_trace(self, postulacion_id: int) -> EvaluationTraceResponse:
        """Contract 14.17: trazabilidad completa con regla_aplicada por item."""
        postulacion = self._get_postulacion(postulacion_id)
        items = self._get_items(postulacion_id)
        reglas = self._get_reglas(postulacion.id_convocatoria)

        # Group items for section-level cap calculation
        items_by_tipo: dict[TipoItemHojaVida, list[ItemHojaVida]] = {}
        for item in items:
            items_by_tipo.setdefault(item.tipo_item, []).append(item)

        # Calculate section totals to apply caps in trace
        section_totals: dict[TipoItemHojaVida, float] = {}
        section_capped: dict[TipoItemHojaVida, float] = {}
        for tipo_item, regla in reglas.items():
            section_items = items_by_tipo.get(tipo_item, [])
            if not section_items:
                continue
            cantidad = sum(
                item.cantidad if item.cantidad and item.cantidad > 0 else 1
                for item in section_items
            )
            puntaje_bruto = cantidad * regla.puntaje_unitario
            section_totals[tipo_item] = puntaje_bruto
            if regla.maximo_acumulable is not None:
                section_capped[tipo_item] = min(puntaje_bruto, regla.maximo_acumulable)
            else:
                section_capped[tipo_item] = puntaje_bruto

        trace_items: list[EvaluationTraceItem] = []
        advertencias: list[str] = []

        for item in items:
            regla = reglas.get(item.tipo_item)
            item_cantidad = item.cantidad if item.cantidad and item.cantidad > 0 else 1

            if regla:
                # Calculate the item's share of the capped section total
                section_total = section_totals.get(item.tipo_item, 0)
                section_final = section_capped.get(item.tipo_item, 0)
                if section_total > 0:
                    item_puntaje = round(
                        (item_cantidad / section_total) * section_final, 2
                    )
                else:
                    item_puntaje = 0.0

                trace_items.append(
                    EvaluationTraceItem(
                        id_item=item.id_item,
                        tipo_item=item.tipo_item,
                        descripcion=item.descripcion,
                        cantidad=item_cantidad,
                        puntaje_unitario=float(regla.puntaje_unitario),
                        maximo_acumulable=(
                            float(regla.maximo_acumulable) if regla.maximo_acumulable else None
                        ),
                        puntaje_asignado=item_puntaje,
                        regla_aplicada=ReglaAplicadaInfo(
                            id_regla=regla.id_regla,
                            descripcion_regla=regla.descripcion_regla,
                        ),
                    )
                )
            else:
                # Item without rule (14.13, 14.14)
                trace_items.append(
                    EvaluationTraceItem(
                        id_item=item.id_item,
                        tipo_item=item.tipo_item,
                        descripcion=item.descripcion,
                        cantidad=item_cantidad,
                        puntaje_unitario=0.0,
                        maximo_acumulable=None,
                        puntaje_asignado=0.0,
                        sin_regla=True,
                    )
                )
                advertencias.append(
                    f"Item #{item.id_item} ({item.tipo_item.value}): sin regla de evaluacion"
                )

        return EvaluationTraceResponse(
            id_postulacion=postulacion_id,
            id_convocatoria=postulacion.id_convocatoria,
            puntaje_total=float(postulacion.puntaje_total) if postulacion.puntaje_total else 0.0,
            detalle_evaluacion=trace_items,
            advertencias=advertencias,
        )

    def _get_postulacion(self, postulacion_id: int) -> Postulacion:
        statement = select(Postulacion).where(
            Postulacion.id_postulacion == postulacion_id
        )
        postulacion = self.db.scalar(statement)
        if postulacion is None:
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
