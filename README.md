<<<<<<< HEAD
# sign_college_backend
=======
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
4. Ejecutar migraciones:

```bash
alembic upgrade head
```

5. Levantar la API:

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000` y la documentacion en
`http://localhost:8000/docs`.
>>>>>>> 9babd1b (feat: base inicial)
