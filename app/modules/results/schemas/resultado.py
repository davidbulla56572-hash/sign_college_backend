from pydantic import BaseModel


class MyResultsResponse(BaseModel):
    estado: str
    puntaje_total: float | None = None
    resumen: str
