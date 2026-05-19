from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_active_user
from app.db.models.user import Usuario
from app.modules.results.schemas.resultado import MyResultsResponse

router = APIRouter()


@router.get("/mis-resultados", response_model=MyResultsResponse)
def get_my_results(_: Usuario = Depends(get_current_active_user)) -> MyResultsResponse:
    return MyResultsResponse(
        estado="SIN_POSTULACION",
        puntaje_total=None,
        resumen="No hay resultados disponibles para el usuario autenticado.",
    )
