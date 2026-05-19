# Sign College Backend

API REST para el sistema inteligente de evaluacion de aspirantes docentes.

## Stack base

- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pydantic v2
- JWT con `python-jose`
- `passlib[bcrypt]`
- pytest

## Arranque local

1. Crear y activar un entorno virtual de Python 3.11+.
2. Instalar dependencias:

```bash
pip install -e ".[dev]"
```

3. Copiar `.env.example` a `.env` y ajustar la conexion PostgreSQL.
4. Levantar PostgreSQL local si usas Docker:

```bash
docker compose up -d postgres
```

5. Ejecutar migraciones:

```bash
alembic upgrade head
```

6. Crear usuarios de desarrollo:

```bash
python -m app.db.seed
```

Credenciales de prueba:

- Admin: `admin@signcollege.com` / `Admin12345!`
- Aspirante: `aspirante@signcollege.com` / `Aspirante12345!`

7. Levantar la API:

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000` y la documentacion en
`http://localhost:8000/docs`.

## Base tecnica de Fase 2

- Router versionado con prefijo `/api/v1`.
- Health check en `/api/v1/health`.
- Contratos base preparados para auth, users, convocatorias, postulaciones, hoja de vida y resultados.
- Settings centralizados con Pydantic Settings.
- SQLAlchemy y Alembic configurados para PostgreSQL.
- Migracion inicial del modelo de dominio.
- Manejo uniforme de errores controlados, validacion, HTTP, base de datos y errores inesperados.

## Flujo funcional de Fase 3

- `POST /api/v1/auth/login` valida email y contrasena contra usuarios persistidos.
- `GET /api/v1/auth/me` devuelve el usuario autenticado a partir del token Bearer.
- `get_current_active_user` y `require_admin_role` quedan listos para proteger modulos.
- Los endpoints privados base usan token Bearer y responden 401/403 de forma consistente.
