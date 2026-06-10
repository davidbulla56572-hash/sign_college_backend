from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.db.models.user import Usuario
from app.integrations.gemini.cv_extraction_client import create_extraction_provider
from app.integrations.storage.local_storage import LocalDocumentStorage
from app.modules.cv_processing.normalization import CVNormalizationService
from app.modules.cv_processing.repository import HojaVidaRepository
from app.modules.cv_processing.schemas.hoja_vida import (
    HojaVidaDraftResponse,
    HojaVidaProcesadaResponse,
    HojaVidaSavePayload,
    HojaVidaSaveResponse,
    SoporteItemResponse,
)
from app.modules.cv_processing.service import HojaVidaService

router = APIRouter()


def get_hoja_vida_service(db: Session = Depends(get_db)) -> HojaVidaService:
    return HojaVidaService(
        repository=HojaVidaRepository(db),
        extraction_provider=create_extraction_provider(),
        storage=LocalDocumentStorage(),
        normalizer=CVNormalizationService(),
    )


@router.get("/postulaciones/{postulacion_id}", response_model=HojaVidaDraftResponse)
def get_hoja_vida_draft(
    postulacion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: HojaVidaService = Depends(get_hoja_vida_service),
) -> HojaVidaDraftResponse:
    """Load persisted draft for rehydration."""
    draft = service.get_draft_hoja_vida(current_user, postulacion_id)
    if draft is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("No se encontro borrador de hoja de vida")
    return draft


@router.post(
    "/postulaciones/{postulacion_id}/upload",
    response_model=HojaVidaProcesadaResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_cv_within_postulacion(
    postulacion_id: int,
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_active_user),
    service: HojaVidaService = Depends(get_hoja_vida_service),
) -> HojaVidaProcesadaResponse:
    """Upload and process CV within a specific postulacion."""
    postulacion = service.repository.get_postulacion_for_user(
        postulacion_id=postulacion_id,
        user_id=current_user.id_usuario,
    )
    if postulacion is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Postulacion not found for current user")

    content = await file.read()
    return service.process_upload(
        user=current_user,
        postulacion_id=postulacion_id,
        filename=file.filename or "cv",
        content_type=file.content_type,
        content=content,
    )


@router.put("/postulaciones/{postulacion_id}", response_model=HojaVidaSaveResponse)
def save_hoja_vida(
    postulacion_id: int,
    payload: HojaVidaSavePayload,
    current_user: Usuario = Depends(get_current_active_user),
    service: HojaVidaService = Depends(get_hoja_vida_service),
) -> HojaVidaSaveResponse:
    return service.save_structured_data(
        user=current_user,
        postulacion_id=postulacion_id,
        payload=payload,
    )


@router.post(
    "/items/{item_id}/soportes",
    response_model=SoporteItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_item_support(
    item_id: int,
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_active_user),
    service: HojaVidaService = Depends(get_hoja_vida_service),
) -> SoporteItemResponse:
    content = await file.read()
    return service.upload_item_support(
        user=current_user,
        item_id=item_id,
        filename=file.filename or "soporte",
        content_type=file.content_type,
        content=content,
    )


@router.get("/items/{item_id}/soportes", response_model=list[SoporteItemResponse])
def list_item_supports(
    item_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: HojaVidaService = Depends(get_hoja_vida_service),
) -> list[SoporteItemResponse]:
    return service.list_item_supports(current_user, item_id)


@router.get("/soportes/{soporte_id}", response_model=SoporteItemResponse)
def get_support_detail(
    soporte_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: HojaVidaService = Depends(get_hoja_vida_service),
) -> SoporteItemResponse:
    return service.get_support_detail(current_user, soporte_id)


@router.delete("/soportes/{soporte_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_support(
    soporte_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    service: HojaVidaService = Depends(get_hoja_vida_service),
) -> None:
    service.delete_support(current_user, soporte_id)
