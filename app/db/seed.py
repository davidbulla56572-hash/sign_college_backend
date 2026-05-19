from sqlalchemy import select

from app.core.security import hash_password
from app.db.models.user import UserRole, Usuario
from app.db.session import SessionLocal

DEV_USERS = [
    {
        "nombre": "Admin",
        "apellido": "Principal",
        "cedula": "1000000001",
        "email": "admin@signcollege.test",
        "telefono": "3000000001",
        "municipio": "Bogota",
        "departamento": "Cundinamarca",
        "pais": "Colombia",
        "rol": UserRole.ADMIN,
        "password": "Admin12345!",
    },
    {
        "nombre": "Aspirante",
        "apellido": "Demo",
        "cedula": "1000000002",
        "email": "aspirante@signcollege.test",
        "telefono": "3000000002",
        "municipio": "Bogota",
        "departamento": "Cundinamarca",
        "pais": "Colombia",
        "rol": UserRole.ASPIRANTE,
        "password": "Aspirante12345!",
    },
]


def upsert_dev_users() -> None:
    with SessionLocal() as db:
        for user_data in DEV_USERS:
            values = user_data.copy()
            password = values.pop("password")
            statement = select(Usuario).where(Usuario.email == values["email"])
            user = db.scalar(statement)

            if user is None:
                db.add(Usuario(**values, password_hash=hash_password(password)))
                continue

            for field, value in values.items():
                setattr(user, field, value)
            user.password_hash = hash_password(password)

        db.commit()


if __name__ == "__main__":
    upsert_dev_users()
    print("Development users are ready.")
