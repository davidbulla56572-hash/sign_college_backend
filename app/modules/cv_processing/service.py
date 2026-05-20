from pathlib import Path

from app.core.config import settings
from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.db.models.user import Usuario
from app.integrations.gemini.cv_extraction_client import CVExtractionProvider
from app.integrations.storage.local_storage import LocalDocumentStorage
from app.modules.cv_processing.normalization import CVNormalizationService
from app.modules.cv_processing.repository import HojaVidaRepository
from app.modules.cv_processing.schemas.hoja_vida import (
    DatosPersonalesHojaVida,
    DocumentoProcesado,
    HojaVidaDraftResponse,
    HojaVidaItemPayload,
    HojaVidaItemsPayload,
    HojaVidaProcesadaResponse,
    HojaVidaSavePayload,
    HojaVidaSaveResponse,
)


class InvalidCVFileError(AppError):
    status_code = 400
    code = "invalid_cv_file"


class HojaVidaService:
    allowed_extensions = {".pdf"}
    allowed_content_types = {"application/pdf"}

    def __init__(
        self,
        repository: HojaVidaRepository,
        extraction_provider: CVExtractionProvider,
        storage: LocalDocumentStorage,
        normalizer: CVNormalizationService,
    ) -> None:
        self.repository = repository
        self.extraction_provider = extraction_provider
        self.storage = storage
        self.normalizer = normalizer

    def process_upload(
        self,
        user: Usuario,
        postulacion_id: int,
        filename: str,
        content_type: str | None,
        content: bytes,
    ) -> HojaVidaProcesadaResponse:
        self._validate_file(filename, content_type, content)

        if user.rol.value != "ASPIRANTE":
            raise ForbiddenError("Only aspirants can upload hoja de vida data")

        postulacion = self.repository.get_postulacion_for_user(
            postulacion_id=postulacion_id,
            user_id=user.id_usuario,
        )
        if postulacion is None:
            raise NotFoundError("Postulacion not found for current user")

        stored_url = self.storage.save_cv(user.id_usuario, filename, content)
        raw_payload = self.extraction_provider.extract(
            filename=filename,
            content_type=content_type or "application/octet-stream",
            content=content,
        )
        datos_personales = self.normalizer.normalize_personal_data(raw_payload, user)
        items = self.normalizer.normalize_items(raw_payload)
        metadata = self.normalizer.normalize_metadata(raw_payload)

        postulacion.url_cv_original = stored_url
        self.repository.update_user_personal_data(user, datos_personales)
        self.repository.replace_hoja_vida_items(postulacion, items)
        self.repository.commit()

        return HojaVidaProcesadaResponse(
            postulacion_id=postulacion.id_postulacion,
            documento=DocumentoProcesado(
                nombre_archivo=filename,
                tipo_archivo=content_type or "application/octet-stream",
                tamanio_bytes=len(content),
                url_archivo=stored_url,
            ),
            datos_personales=datos_personales,
            items=items,
            metadata_extraccion=metadata,
        )

    def save_structured_data(
        self,
        user: Usuario,
        postulacion_id: int,
        payload: HojaVidaSavePayload,
    ) -> HojaVidaSaveResponse:
        postulacion = self.repository.get_postulacion_for_user(
            postulacion_id=postulacion_id,
            user_id=user.id_usuario,
        )
        if postulacion is None:
            raise NotFoundError("Postulacion not found for current user")

        if user.rol.value != "ASPIRANTE":
            raise ForbiddenError("Only aspirants can save hoja de vida data")

        if payload.documento:
            postulacion.url_cv_original = payload.documento.url_archivo

        self.repository.update_user_personal_data(user, payload.datos_personales)
        total_items = self.repository.replace_hoja_vida_items(postulacion, payload.items)
        self.repository.commit()

        return HojaVidaSaveResponse(
            id_postulacion=postulacion.id_postulacion,
            estado=postulacion.estado.value,
            total_items=total_items,
            message="Hoja de vida guardada correctamente.",
        )

    def get_draft_hoja_vida(
        self,
        user: Usuario,
        postulacion_id: int,
    ) -> HojaVidaDraftResponse | None:
        """Load persisted draft for rehydration."""
        draft = self.repository.get_draft_hoja_vida(user.id_usuario, postulacion_id)
        if draft is None:
            return None

        postulacion = draft["postulacion"]
        convocatoria = draft["convocatoria"]
        items_db = draft["items"]

        section_map = self._db_section_map()
        items = HojaVidaItemsPayload(**{k: [] for k in section_map})
        for item_db in items_db:
            section_key = section_map.get(item_db.tipo_item)
            if section_key:
                getattr(items, section_key).append(
                    HojaVidaItemPayload(
                        descripcion=item_db.descripcion,
                        institucion=item_db.institucion,
                        fecha_inicio=item_db.fecha_inicio,
                        fecha_fin=item_db.fecha_fin,
                        cantidad=item_db.cantidad,
                    )
                )

        datos_personales = DatosPersonalesHojaVida(
            nombre=user.nombre,
            apellido=user.apellido,
            email=user.email,
            telefono=user.telefono,
            municipio=user.municipio,
            departamento=user.departamento,
            pais=user.pais or "Colombia",
        )

        return HojaVidaDraftResponse(
            id_postulacion=postulacion.id_postulacion,
            id_convocatoria=postulacion.id_convocatoria,
            titulo_convocatoria=convocatoria.titulo,
            estado=postulacion.estado.value,
            url_cv_original=postulacion.url_cv_original,
            datos_personales=datos_personales,
            items=items,
        )

    def _db_section_map(self) -> dict:
        from app.db.models.hoja_vida import TipoItemHojaVida
        return {
            TipoItemHojaVida.FORMACION: "formacion",
            TipoItemHojaVida.EXPERIENCIA: "experiencia",
            TipoItemHojaVida.PRODUCCION: "produccion",
            TipoItemHojaVida.PONENCIA: "ponencia",
            TipoItemHojaVida.INVESTIGACION: "investigacion",
        }

    def _validate_file(
        self,
        filename: str,
        content_type: str | None,
        content: bytes,
    ) -> None:
        extension = Path(filename or "").suffix.lower()
        if extension not in self.allowed_extensions:
            raise InvalidCVFileError("Solo se aceptan archivos PDF")

        if content_type and content_type not in self.allowed_content_types:
            raise InvalidCVFileError("File content type is not allowed")

        if not content:
            raise InvalidCVFileError("File is empty")

        if len(content) > settings.upload_max_bytes:
            raise InvalidCVFileError("File exceeds the maximum allowed size")
