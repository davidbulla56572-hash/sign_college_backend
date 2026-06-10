from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.db.models.user import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.modules.auth.service import AuthService
from app.modules.users.schemas.user import UserResponse

router = APIRouter()


def _get_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(_get_service),
) -> AuthResponse:
    return service.login(payload)


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    payload: RegisterRequest,
    service: AuthService = Depends(_get_service),
) -> AuthResponse:
    return service.register(payload)


@router.get("/me", response_model=UserResponse)
def me(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    return current_user
