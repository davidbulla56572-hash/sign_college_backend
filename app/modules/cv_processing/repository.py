from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models.convocatoria import Convocatoria
from app.db.models.hoja_vida import ItemHojaVida, TipoItemHojaVida
from app.db.models.postulacion import Postulacion, PostulacionEstado
from app.db.models.user import UserRole, Usuario
from app.modules.cv_processing.schemas.hoja_vida import (
    DatosPersonalesHojaVida,
    HojaVidaItemPayload,
    HojaVidaItemsPayload,
)


class HojaVidaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_postulacion_for_user(
        self,
        postulacion_id: int,
        user_id: int,
    ) -> Postulacion | None:
        statement = select(Postulacion).where(
            Postulacion.id_postulacion == postulacion_id,
            Postulacion.id_usuario == user_id,
        )
        return self.db.scalar(statement)

    def ensure_draft_postulacion(self, user: Usuario, cv_url: str | None = None) -> Postulacion:
        convocatoria = self._ensure_active_convocatoria(user)
        statement = select(Postulacion).where(
            Postulacion.id_usuario == user.id_usuario,
            Postulacion.id_convocatoria == convocatoria.id_convocatoria,
        )
        postulacion = self.db.scalar(statement)

        if postulacion is None:
            postulacion = Postulacion(
                id_usuario=user.id_usuario,
                id_convocatoria=convocatoria.id_convocatoria,
                estado=PostulacionEstado.BORRADOR,
                url_cv_original=cv_url,
            )
            self.db.add(postulacion)
            self.db.flush()
            return postulacion

        if cv_url:
            postulacion.url_cv_original = cv_url
        return postulacion

    def update_user_personal_data(
        self,
        user: Usuario,
        data: DatosPersonalesHojaVida,
    ) -> None:
        user.nombre = data.nombre
        user.apellido = data.apellido
        if data.email:
            user.email = str(data.email)
        user.telefono = data.telefono
        user.municipio = data.municipio
        user.departamento = data.departamento
        user.pais = data.pais

    def replace_hoja_vida_items(
        self,
        postulacion: Postulacion,
        items: HojaVidaItemsPayload,
    ) -> int:
        self.db.execute(
            delete(ItemHojaVida).where(
                ItemHojaVida.id_postulacion == postulacion.id_postulacion
            )
        )

        total = 0
        for section_name, tipo_item in self._section_type_map().items():
            section_items = getattr(items, section_name)
            for item in section_items:
                self.db.add(self._build_item(postulacion.id_postulacion, tipo_item, item))
                total += 1

        return total

    def commit(self) -> None:
        self.db.commit()

    def get_draft_hoja_vida(
        self,
        user_id: int,
        postulacion_id: int,
    ) -> dict | None:
        statement = select(Postulacion).where(
            Postulacion.id_postulacion == postulacion_id,
            Postulacion.id_usuario == user_id,
            Postulacion.estado.in_([PostulacionEstado.BORRADOR, PostulacionEstado.ENVIADA]),
        )
        postulacion = self.db.scalar(statement)
        if postulacion is None:
            return None

        convocatoria = self.db.scalar(
            select(Convocatoria).where(
                Convocatoria.id_convocatoria == postulacion.id_convocatoria
            )
        )
        if convocatoria is None:
            return None

        items_stmt = select(ItemHojaVida).where(
            ItemHojaVida.id_postulacion == postulacion.id_postulacion
        )
        items = list(self.db.scalars(items_stmt).all())

        return {
            "postulacion": postulacion,
            "convocatoria": convocatoria,
            "items": items,
        }

    def _build_item(
        self,
        postulacion_id: int,
        tipo_item: TipoItemHojaVida,
        item: HojaVidaItemPayload,
    ) -> ItemHojaVida:
        return ItemHojaVida(
            id_postulacion=postulacion_id,
            tipo_item=tipo_item,
            descripcion=item.descripcion,
            institucion=item.institucion,
            fecha_inicio=item.fecha_inicio,
            fecha_fin=item.fecha_fin,
            cantidad=item.cantidad,
        )

    def _ensure_active_convocatoria(self, user: Usuario) -> Convocatoria:
        statement = select(Convocatoria).where(Convocatoria.activa.is_(True)).limit(1)
        convocatoria = self.db.scalar(statement)
        if convocatoria is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(
                "No hay convocatorias activas disponibles para postularse."
            )
        return convocatoria

    def _get_admin_user_id(self) -> int | None:
        statement = select(Usuario.id_usuario).where(Usuario.rol == UserRole.ADMIN).limit(1)
        return self.db.scalar(statement)

    def _section_type_map(self) -> dict[str, TipoItemHojaVida]:
        return {
            "formacion": TipoItemHojaVida.FORMACION,
            "experiencia": TipoItemHojaVida.EXPERIENCIA,
            "produccion": TipoItemHojaVida.PRODUCCION,
            "ponencia": TipoItemHojaVida.PONENCIA,
            "investigacion": TipoItemHojaVida.INVESTIGACION,
        }
