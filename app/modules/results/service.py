"""Service for aspirant-facing results (Fase 15)."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.db.models.convocatoria import Convocatoria
from app.db.models.hoja_vida import ItemHojaVida
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.modules.results.schemas.resultado import (
    MiResultadoResponse,
    PostulacionStatusResponse,
    ResumenEvaluacion,
)

# -- Fase 15: Mapeo de estados a labels, colores y mensajes contextuales --

ESTADO_LABELS: dict[PostulacionEstado, str] = {
    PostulacionEstado.BORRADOR: "Borrador",
    PostulacionEstado.ENVIADA: "Enviada",
    PostulacionEstado.EN_EVALUACION: "En evaluacion",
    PostulacionEstado.EVALUADA: "Evaluada",
    PostulacionEstado.RECHAZADA: "Rechazada",
}

ESTADO_COLORS: dict[PostulacionEstado, str] = {
    PostulacionEstado.BORRADOR: "gray",
    PostulacionEstado.ENVIADA: "blue",
    PostulacionEstado.EN_EVALUACION: "amber",
    PostulacionEstado.EVALUADA: "green",
    PostulacionEstado.RECHAZADA: "red",
}

ESTADO_MENSAJES: dict[PostulacionEstado, str] = {
    PostulacionEstado.BORRADOR: "Tu postulacion aun no ha sido enviada. Completala y enviala cuando estes listo.",
    PostulacionEstado.ENVIADA: "Tu postulacion fue enviada y esta pendiente de evaluacion. Pronto tendremos noticias.",
    PostulacionEstado.EN_EVALUACION: "Tu postulacion se encuentra actualmente en evaluacion. Estamos revisando tu informacion.",
    PostulacionEstado.EVALUADA: "Tu postulacion ha sido evaluada. Puedes ver tu puntaje y el detalle a continuacion.",
    PostulacionEstado.RECHAZADA: "Tu postulacion no fue seleccionada en esta convocatoria. Gracias por participar.",
}

# Labels amigables para tipos de item
TIPO_ITEM_LABELS: dict[str, str] = {
    "FORMACION": "Formacion academica",
    "EXPERIENCIA": "Experiencia profesional",
    "PRODUCCION": "Produccion academica",
    "PONENCIA": "Ponencias y conferencias",
    "INVESTIGACION": "Investigacion",
    "DOCUMENTO": "Documentos",
    "OTRO": "Otros",
}


class ResultsService:
    """Servicio de resultados orientado al aspirante (Fase 15).

    Expone el resultado tecnico del sistema como una experiencia
    comprensible: estado legible, puntaje con contexto, resumen por
    seccion y mensajes contextuales.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -- Status endpoint (15.15) --

    def get_postulacion_status(
        self, postulacion_id: int, usuario_id: int
    ) -> PostulacionStatusResponse:
        """Devuelve el estado legible de una postulacion (15.15)."""
        postulacion = self._get_postulacion_owner(postulacion_id, usuario_id)
        estado = postulacion.estado

        titulo_conv = ""
        if postulacion.convocatoria:
            titulo_conv = postulacion.convocatoria.titulo

        return PostulacionStatusResponse(
            id_postulacion=postulacion.id_postulacion,
            estado=estado.value,
            estado_label=ESTADO_LABELS.get(estado, estado.value),
            estado_color=ESTADO_COLORS.get(estado, "gray"),
            mensaje_contextual=ESTADO_MENSAJES.get(estado, ""),
            id_convocatoria=postulacion.id_convocatoria,
            titulo_convocatoria=titulo_conv,
            fecha_envio=_format_dt(postulacion.fecha_envio),
            fecha_evaluacion=_format_dt(postulacion.fecha_evaluacion),
        )

    # -- Mis resultados (15.15, 15.16) --

    def get_mis_resultados(
        self, usuario_id: int
    ) -> list[MiResultadoResponse]:
        """Lista de resultados del aspirante con contexto completo (15.16)."""
        statement = (
            select(Postulacion)
            .where(Postulacion.id_usuario == usuario_id)
            .options(joinedload(Postulacion.convocatoria))
            .order_by(Postulacion.fecha_creacion.desc())
        )
        postulaciones = list(self.db.scalars(statement).all())

        return [
            self._build_mi_resultado(p) for p in postulaciones
        ]

    # -- Detalle de una postulacion (15.15) --

    def get_resultado_detalle(
        self, postulacion_id: int, usuario_id: int
    ) -> MiResultadoResponse:
        """Detalle de resultado de una postulacion especifica (15.16)."""
        postulacion = self._get_postulacion_owner(postulacion_id, usuario_id)
        return self._build_mi_resultado(postulacion)

    # -- Helpers --

    def _get_postulacion_owner(
        self, postulacion_id: int, usuario_id: int
    ) -> Postulacion:
        statement = (
            select(Postulacion)
            .where(
                Postulacion.id_postulacion == postulacion_id,
                Postulacion.id_usuario == usuario_id,
            )
            .options(joinedload(Postulacion.convocatoria))
        )
        postulacion = self.db.scalar(statement)
        if postulacion is None:
            raise NotFoundError("Postulacion not found")
        return postulacion

    def _build_mi_resultado(
        self, postulacion: Postulacion
    ) -> MiResultadoResponse:
        estado = postulacion.estado
        titulo_conv = ""
        if postulacion.convocatoria:
            titulo_conv = postulacion.convocatoria.titulo

        # Fetch items for resumen and detalle
        items = list(
            self.db.scalars(
                select(ItemHojaVida).where(
                    ItemHojaVida.id_postulacion == postulacion.id_postulacion
                )
            ).all()
        )

        # Build resumen_evaluacion: group by tipo_item, sum puntaje_asignado
        resumen_map: dict[str, dict] = {}
        for item in items:
            tipo = item.tipo_item.value
            if tipo not in resumen_map:
                resumen_map[tipo] = {
                    "tipo_item": tipo,
                    "label": TIPO_ITEM_LABELS.get(tipo, tipo),
                    "puntaje_obtenido": 0.0,
                    "cantidad_items": 0,
                }
            resumen_map[tipo]["puntaje_obtenido"] += float(
                item.puntaje_asignado or 0.0
            )
            resumen_map[tipo]["cantidad_items"] += 1

        resumen_evaluacion = [
            ResumenEvaluacion(
                tipo_item=r["tipo_item"],
                label=r["label"],
                puntaje_obtenido=round(r["puntaje_obtenido"], 2),
                cantidad_items=r["cantidad_items"],
            )
            for r in resumen_map.values()
        ]

        # Build detalle
        detalle = [
            {
                "id_item": item.id_item,
                "tipo_item": item.tipo_item.value,
                "descripcion": item.descripcion,
                "puntaje_asignado": float(item.puntaje_asignado or 0.0),
            }
            for item in items
        ]

        return MiResultadoResponse(
            id_postulacion=postulacion.id_postulacion,
            estado=estado.value,
            estado_label=ESTADO_LABELS.get(estado, estado.value),
            estado_color=ESTADO_COLORS.get(estado, "gray"),
            mensaje_contextual=ESTADO_MENSAJES.get(estado, ""),
            puntaje_total=(
                float(postulacion.puntaje_total)
                if postulacion.puntaje_total is not None
                else None
            ),
            fecha_evaluacion=_format_dt(postulacion.fecha_evaluacion),
            convocatoria={
                "id_convocatoria": postulacion.id_convocatoria,
                "titulo": titulo_conv,
            },
            resumen_evaluacion=resumen_evaluacion,
            detalle=detalle,
        )


def _format_dt(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()
