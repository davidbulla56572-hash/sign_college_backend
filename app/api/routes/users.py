from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_active_user
from app.db.models.user import Usuario
from app.modules.users.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    return current_user
