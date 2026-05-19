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

## Endpoints completos

### Autenticacion
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/login` | Login | Publico |
| GET | `/api/v1/auth/me` | Usuario actual | Any |

### Convocatorias
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/convocatorias` | Convocatorias activas | Publico |
| GET | `/api/v1/convocatorias/todas` | Todas (admin) | Admin |
| GET | `/api/v1/convocatorias/{id}` | Detalle | Publico |
| POST | `/api/v1/convocatorias` | Crear | Admin |
| PATCH | `/api/v1/convocatorias/{id}` | Actualizar | Admin |
| POST | `/api/v1/convocatorias/{id}/toggle` | Activar/cerrar | Admin |

### Postulaciones
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/postulaciones` | Crear postulacion | Any |
| GET | `/api/v1/postulaciones/mine` | Mis postulaciones | Any |
| GET | `/api/v1/postulaciones/mine/{id}` | Detalle propia | Any |
| POST | `/api/v1/postulaciones/mine/{id}/submit` | Enviar postulacion | Any |
| GET | `/api/v1/postulaciones/todas` | Todas (con filtro) | Admin |
| GET | `/api/v1/postulaciones/{id}` | Detalle | Admin |
| PATCH | `/api/v1/postulaciones/{id}/estado` | Cambiar estado | Admin |

### Hoja de Vida
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/hoja-vida/upload` | Subir CV | Any |
| PUT | `/api/v1/hoja-vida/postulaciones/{id}` | Guardar datos | Any |

### Reglas de Evaluacion
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/reglas/convocatorias/{id}` | Listar reglas | Publico |
| POST | `/api/v1/reglas/convocatorias/{id}` | Crear regla | Admin |
| PATCH | `/api/v1/reglas/{id}` | Actualizar regla | Admin |
| DELETE | `/api/v1/reglas/{id}` | Eliminar regla | Admin |

### Resultados
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/resultados/mis-resultados` | Mis resultados | Any |
| GET | `/api/v1/resultados/{id}` | Detalle resultado | Any |
| POST | `/api/v1/resultados/{id}/evaluar` | Evaluar postulacion | Admin |
| GET | `/api/v1/resultados/ranking/{id}` | Ranking | Admin |

### Admin
| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/admin/aspirantes` | Lista aspirantes | Admin |
| GET | `/api/v1/admin/aspirantes/{id}` | Detalle aspirante | Admin |
| GET | `/api/v1/admin/postulaciones/{id}/detalle` | Detalle con soportes | Admin |

## Base tecnica

- Router versionado con prefijo `/api/v1`.
- Health check en `/api/v1/health`.
- Settings centralizados con Pydantic Settings.
- SQLAlchemy y Alembic configurados para PostgreSQL.
- Manejo uniforme de errores controlados, validacion, HTTP, base de datos y errores inesperados.

## Motor de evaluacion

La logica de evaluacion esta encapsulada en `EvaluationService` (`app/modules/evaluation/service.py`):

- Obtiene reglas de la convocatoria
- Agrupa items de hoja de vida por tipo
- Calcula puntaje por seccion aplicando maximos acumulables
- Persiste `puntaje_asignado` en cada item
- Actualiza `puntaje_total` y `estado` de la postulacion
- Registra `fecha_evaluacion`

## Testing

```bash
pytest tests/ -v
```

## Flujo funcional completo

1. Aspirante sube hoja de vida (PDF/DOCX)
2. Backend procesa y extrae informacion (mock IA)
3. Aspirante edita y guarda datos estructurados
4. Aspirante envia postulacion
5. Admin ejecuta evaluacion (`POST /resultados/{id}/evaluar`)
6. Motor calcula puntajes aplicando reglas de convocatoria
7. Aspirante consulta resultados
8. Admin consulta ranking y detalle
