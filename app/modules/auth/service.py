from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas.auth import AuthResponse, LoginRequest
from app.modules.users.schemas.user import UserResponse


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    def login(self, payload: LoginRequest) -> AuthResponse:
        user = self.repository.get_by_email(str(payload.email))
        if user is None or not user.activo:
            raise UnauthorizedError("Invalid credentials")

        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        access_token = create_access_token(
            subject=str(user.id_usuario),
            extra_claims={"role": user.rol.value},
        )
        return AuthResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )
