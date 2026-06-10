from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.models.convocatoria import Convocatoria, ConvocatoriaEstado
from app.db.models.hoja_vida import ItemHojaVida, SoporteItem, TipoItemHojaVida
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
        current_items = list(
            self.db.scalars(
                select(ItemHojaVida).where(
                    ItemHojaVida.id_postulacion == postulacion.id_postulacion
                )
            ).all()
        )
        current_by_id = {item.id_item: item for item in current_items}
        kept_ids: set[int] = set()
        total = 0
        for section_name, tipo_item in self._section_type_map().items():
            section_items = getattr(items, section_name)
            for item in section_items:
                if item.id_item is not None and item.id_item in current_by_id:
                    db_item = current_by_id[item.id_item]
                    db_item.tipo_item = tipo_item
                    db_item.descripcion = item.descripcion
                    db_item.institucion = item.institucion
                    db_item.fecha_inicio = item.fecha_inicio
                    db_item.fecha_fin = item.fecha_fin
                    db_item.cantidad = item.cantidad
                    kept_ids.add(db_item.id_item)
                else:
                    self.db.add(self._build_item(postulacion.id_postulacion, tipo_item, item))
                total += 1

        removed_ids = [
            item.id_item for item in current_items if item.id_item not in kept_ids
        ]
        if removed_ids:
            self.db.execute(delete(SoporteItem).where(SoporteItem.id_item.in_(removed_ids)))
            self.db.execute(delete(ItemHojaVida).where(ItemHojaVida.id_item.in_(removed_ids)))

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

    def get_item_for_user(
        self,
        item_id: int,
        user_id: int,
    ) -> ItemHojaVida:
        statement = (
            select(ItemHojaVida)
            .join(Postulacion, Postulacion.id_postulacion == ItemHojaVida.id_postulacion)
            .where(
                ItemHojaVida.id_item == item_id,
                Postulacion.id_usuario == user_id,
                Postulacion.estado.in_([PostulacionEstado.BORRADOR, PostulacionEstado.ENVIADA]),
            )
        )
        item = self.db.scalar(statement)
        if item is None:
            raise NotFoundError("Item de hoja de vida no encontrado para el usuario")
        return item

    def list_soportes_for_item(self, item_id: int) -> list[SoporteItem]:
        statement = (
            select(SoporteItem)
            .where(SoporteItem.id_item == item_id)
            .order_by(SoporteItem.fecha_carga.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_soporte_for_user(self, soporte_id: int, user_id: int) -> SoporteItem:
        statement = (
            select(SoporteItem)
            .join(ItemHojaVida, ItemHojaVida.id_item == SoporteItem.id_item)
            .join(Postulacion, Postulacion.id_postulacion == ItemHojaVida.id_postulacion)
            .where(
                SoporteItem.id_soporte == soporte_id,
                Postulacion.id_usuario == user_id,
            )
        )
        soporte = self.db.scalar(statement)
        if soporte is None:
            raise NotFoundError("Soporte no encontrado para el usuario")
        return soporte

    def create_soporte(
        self,
        item_id: int,
        nombre_archivo: str,
        url_archivo: str,
        tipo_archivo: str,
        tamanio_bytes: int,
    ) -> SoporteItem:
        soporte = SoporteItem(
            id_item=item_id,
            nombre_archivo=nombre_archivo,
            url_archivo=url_archivo,
            tipo_archivo=tipo_archivo,
            tamanio_bytes=tamanio_bytes,
        )
        self.db.add(soporte)
        self.db.flush()
        return soporte

    def delete_soporte(self, soporte: SoporteItem) -> None:
        self.db.delete(soporte)

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
        statement = (
            select(Convocatoria)
            .where(
                Convocatoria.activa.is_(True),
                Convocatoria.estado == ConvocatoriaEstado.ACTIVA,
            )
            .limit(1)
        )
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
