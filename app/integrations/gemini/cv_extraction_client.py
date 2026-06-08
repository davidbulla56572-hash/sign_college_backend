import json
import logging
from typing import Any, Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)


class CVExtractionProvider(Protocol):
    def extract(self, filename: str, content_type: str, content: bytes) -> dict[str, Any]:
        ...


class MockCVExtractionClient:
    """Fallback provider that returns empty structured data."""

    def extract(
        self,
        filename: str,
        content_type: str,
        content: bytes,
        warnings: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "source": "mock",
            "confidence": None,
            "document": {
                "filename": filename,
                "content_type": content_type,
                "size": len(content),
            },
            "personal": {},
            "sections": {
                "formacion": [],
                "experiencia": [],
                "produccion": [],
                "ponencia": [],
                "investigacion": [],
            },
            "warnings": [
                "Extraccion simulada: completa o ajusta los datos antes de guardar.",
                *(warnings or []),
            ],
        }


class GeminiCVExtractionClient:
    """Real Gemini integration for CV extraction.

    Sends the uploaded file to Gemini with a structured prompt asking for
    personal data and academic items classified by type.

    Falls back to mock if the API key is not configured or the call fails.
    """

    _EXTRACTION_PROMPT = """\
Extrae la informacion de esta hoja de vida y responde SOLO con un JSON valido \
sin texto adicional. El JSON debe seguir exactamente esta estructura:

{
  "personal": {
    "nombre": "...",
    "apellido": "...",
    "email": "...",
    "telefono": "...",
    "municipio": "...",
    "departamento": "...",
    "pais": "..."
  },
  "sections": {
    "formacion": [
      {"descripcion": "...", "institucion": "...", "fecha_inicio": "YYYY-MM-DD", "fecha_fin": "YYYY-MM-DD", "cantidad": 1}
    ],
    "experiencia": [
      {"descripcion": "...", "institucion": "...", "fecha_inicio": "YYYY-MM-DD", "fecha_fin": "YYYY-MM-DD", "cantidad": 1}
    ],
    "produccion": [
      {"descripcion": "...", "institucion": "...", "fecha_inicio": "YYYY-MM-DD", "fecha_fin": "YYYY-MM-DD", "cantidad": 1}
    ],
    "ponencia": [
      {"descripcion": "...", "institucion": "...", "fecha_inicio": "YYYY-MM-DD", "fecha_fin": "YYYY-MM-DD", "cantidad": 1}
    ],
    "investigacion": [
      {"descripcion": "...", "institucion": "...", "fecha_inicio": "YYYY-MM-DD", "fecha_fin": "YYYY-MM-DD", "cantidad": 1}
    ]
  }
}

Reglas:
- "formacion": titulos academicos, grados, certificaciones, cursos relevantes
- "experiencia": experiencia laboral, especialmente docente
- "produccion": libros, articulos, publicaciones academicas
- "ponencia": conferencias, eventos academicos donde haya sido ponente
- "investigacion": proyectos de investigacion, grupos de investigacion
- Para cada item, "cantidad" es el numero de items similares si se agrupan, o 1
- Si una seccion no tiene items, deja el array vacio []
- Si un campo de personal no se encuentra, usa null
- Las fechas deben estar en formato "YYYY-MM-DD" o null si no se encuentran
- No inventes informacion. Si no esta en el documento, usa null o array vacio.
"""

    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model

    def extract(
        self,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> dict[str, Any]:
        if not self._api_key:
            logger.info("Gemini API key not configured, falling back to mock")
            return MockCVExtractionClient().extract(
                filename,
                content_type,
                content,
                warnings=["Gemini API key no configurada en el backend."],
            )

        try:
            result = self._call_gemini(filename, content_type, content)
            logger.info(
                "Gemini extraction succeeded: %d items across sections",
                sum(len(v) for v in result.get("sections", {}).values()),
            )
            return result
        except Exception as exc:
            logger.warning("Gemini extraction failed: %s", exc)
            if not settings.gemini_fallback_to_mock:
                raise
            return MockCVExtractionClient().extract(
                filename,
                content_type,
                content,
                warnings=[f"Gemini fallo y se uso fallback mock: {exc}"],
            )

    def _call_gemini(
        self,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> dict[str, Any]:
        from google.genai import Client
        from google.genai.types import Part, GenerateContentConfig

        client = Client(api_key=self._api_key)

        mime_type = content_type or "application/pdf"
        parts = [
            Part.from_bytes(data=content, mime_type=mime_type),
            Part.from_text(text=self._EXTRACTION_PROMPT),
        ]

        response = client.models.generate_content(
            model=self._model,
            contents=parts,
            config=GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response")

        raw_json = response.text.strip()
        logger.debug("Gemini raw response length: %d", len(raw_json))

        # Remove markdown code fences if present
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```", 1)[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
            raw_json = raw_json.rsplit("```", 1)[0].strip()

        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            logger.warning("Gemini returned invalid JSON (first 200 chars): %s", raw_json[:200])
            raise ValueError(f"Gemini returned invalid JSON: {exc}") from exc

        sections = parsed.get("sections", {})
        logger.info(
            "Gemini extracted sections: %s",
            {k: len(v) for k, v in sections.items()},
        )

        return {
            "source": "gemini",
            "confidence": None,
            "document": {
                "filename": filename,
                "content_type": content_type,
                "size": len(content),
            },
            "personal": parsed.get("personal", {}) or {},
            "sections": sections or {},
            "warnings": [],
        }


# Factory: use real Gemini if API key is set, otherwise mock
def create_extraction_provider() -> CVExtractionProvider:
    if settings.gemini_api_key:
        logger.info("Using real Gemini extraction provider (model: %s)", settings.gemini_model)
        return GeminiCVExtractionClient()
    logger.info("Using mock extraction provider (no GEMINI_API_KEY)")
    return MockCVExtractionClient()
