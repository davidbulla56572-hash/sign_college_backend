from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.db.models.user import UserRole


class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    cedula: str
    email: EmailStr
    telefono: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    pais: str | None = None
    rol: UserRole
    activo: bool
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)
