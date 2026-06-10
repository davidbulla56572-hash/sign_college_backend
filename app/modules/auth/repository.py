from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.db.models.user import UserRole, Usuario


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.email == email)
        return self.db.scalar(statement)

    def get_by_cedula(self, cedula: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.cedula == cedula)
        return self.db.scalar(statement)

    def get_by_id(self, user_id: int) -> Usuario | None:
        statement = select(Usuario).where(Usuario.id_usuario == user_id)
        return self.db.scalar(statement)

    def create_user(
        self,
        nombre: str,
        apellido: str,
        cedula: str,
        email: str,
        password_hash: str,
        rol: UserRole = UserRole.ASPIRANTE,
    ) -> Usuario:
        # Check for existing email
        if self.get_by_email(email) is not None:
            raise ConflictError("Ya existe una cuenta con ese correo electronico")
        # Check for existing cedula
        if self.get_by_cedula(cedula) is not None:
            raise ConflictError("Ya existe una cuenta con esa cedula")

        user = Usuario(
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            email=email,
            password_hash=password_hash,
            rol=rol,
            activo=True,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def commit(self) -> None:
        self.db.commit()
