from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps.auth import get_current_active_user
from app.db.models.user import Usuario
from app.modules.cv_processing.schemas.upload import UploadPreparedResponse

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadPreparedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def prepare_cv_upload(
    file: UploadFile = File(...),
    _: Usuario = Depends(get_current_active_user),
) -> UploadPreparedResponse:
    return UploadPreparedResponse(
        filename=file.filename or "cv",
        content_type=file.content_type,
        message="Upload contract ready for CV processing implementation.",
    )
