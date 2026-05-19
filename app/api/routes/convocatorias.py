from fastapi import APIRouter

from app.modules.convocatorias.schemas.convocatoria import ConvocatoriaSummary

router = APIRouter()


@router.get("", response_model=list[ConvocatoriaSummary])
def list_convocatorias() -> list[ConvocatoriaSummary]:
    return []
