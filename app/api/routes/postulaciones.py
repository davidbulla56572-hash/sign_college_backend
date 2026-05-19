from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_active_user
from app.db.models.user import Usuario
from app.modules.postulaciones.schemas.postulacion import PostulacionSummary

router = APIRouter()


@router.get("/mine", response_model=list[PostulacionSummary])
def list_my_postulaciones(
    _: Usuario = Depends(get_current_active_user),
) -> list[PostulacionSummary]:
    return []
