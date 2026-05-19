from collections.abc import Sequence

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.models.user import UserRole, Usuario
from app.modules.auth.repository import AuthRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    payload = decode_access_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise UnauthorizedError("Invalid token subject")

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid token subject") from exc

    user = AuthRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("Authenticated user is not available")
    return user


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if not current_user.activo:
        raise ForbiddenError("User account is inactive")
    return current_user


def require_roles(roles: Sequence[UserRole]):
    def dependency(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        if current_user.rol not in roles:
            raise ForbiddenError("User does not have permission for this resource")
        return current_user

    return dependency


def require_admin_role(
    current_user: Usuario = Depends(require_roles([UserRole.ADMIN])),
) -> Usuario:
    return current_user
