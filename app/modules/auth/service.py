from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import UserRole
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
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

    def register(self, payload: RegisterRequest) -> AuthResponse:
        password_hash = hash_password(payload.password)
        user = self.repository.create_user(
            nombre=payload.nombre,
            apellido=payload.apellido,
            cedula=payload.cedula,
            email=str(payload.email),
            password_hash=password_hash,
            rol=UserRole.ASPIRANTE,
        )
        self.repository.commit()

        access_token = create_access_token(
            subject=str(user.id_usuario),
            extra_claims={"role": user.rol.value},
        )
        return AuthResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )
