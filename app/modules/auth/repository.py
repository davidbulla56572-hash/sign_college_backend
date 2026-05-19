from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import Usuario


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.email == email)
        return self.db.scalar(statement)

    def get_by_id(self, user_id: int) -> Usuario | None:
        statement = select(Usuario).where(Usuario.id_usuario == user_id)
        return self.db.scalar(statement)
