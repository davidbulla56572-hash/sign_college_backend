from fastapi import APIRouter

from app.api.routes import (
    auth,
    convocatorias,
    health,
    hoja_vida,
    postulaciones,
    resultados,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    convocatorias.router,
    prefix="/convocatorias",
    tags=["convocatorias"],
)
api_router.include_router(
    postulaciones.router,
    prefix="/postulaciones",
    tags=["postulaciones"],
)
api_router.include_router(hoja_vida.router, prefix="/hoja-vida", tags=["hoja-vida"])
api_router.include_router(resultados.router, prefix="/resultados", tags=["resultados"])
