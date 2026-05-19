from typing import Any

from app.modules.cv_processing.schemas.hoja_vida import (
    DatosPersonalesHojaVida,
    HojaVidaItemPayload,
    HojaVidaItemsPayload,
    MetadataExtraccion,
)


class CVNormalizationService:
    def normalize_personal_data(
        self,
        raw_payload: dict[str, Any],
        fallback_user: Any,
    ) -> DatosPersonalesHojaVida:
        raw_personal = raw_payload.get("personal") or {}
        return DatosPersonalesHojaVida(
            nombre=raw_personal.get("nombre") or fallback_user.nombre,
            apellido=raw_personal.get("apellido") or fallback_user.apellido,
            email=raw_personal.get("email") or fallback_user.email,
            telefono=raw_personal.get("telefono") or fallback_user.telefono,
            municipio=raw_personal.get("municipio") or fallback_user.municipio,
            departamento=raw_personal.get("departamento") or fallback_user.departamento,
            pais=raw_personal.get("pais") or fallback_user.pais or "Colombia",
        )

    def normalize_items(self, raw_payload: dict[str, Any]) -> HojaVidaItemsPayload:
        raw_sections = raw_payload.get("sections") or {}
        return HojaVidaItemsPayload(
            formacion=self._normalize_section(raw_sections.get("formacion")),
            experiencia=self._normalize_section(raw_sections.get("experiencia")),
            produccion=self._normalize_section(raw_sections.get("produccion")),
            ponencia=self._normalize_section(raw_sections.get("ponencia")),
            investigacion=self._normalize_section(raw_sections.get("investigacion")),
        )

    def normalize_metadata(self, raw_payload: dict[str, Any]) -> MetadataExtraccion:
        return MetadataExtraccion(
            origen=raw_payload.get("source") or "unknown",
            confidence=raw_payload.get("confidence"),
            warnings=list(raw_payload.get("warnings") or []),
        )

    def _normalize_section(self, value: Any) -> list[HojaVidaItemPayload]:
        if not isinstance(value, list):
            return []

        normalized: list[HojaVidaItemPayload] = []
        for item in value:
            if not isinstance(item, dict):
                continue

            # Try multiple possible field names for description
            description = (
                item.get("descripcion")
                or item.get("description")
                or item.get("titulo")
                or item.get("title")
                or item.get("descripcion_corta")
                or ""
            )
            if not description:
                continue

            normalized.append(
                HojaVidaItemPayload(
                    descripcion=description,
                    institucion=(
                        item.get("institucion")
                        or item.get("institution")
                        or item.get("empresa")
                        or item.get("organization")
                        or item.get("universidad")
                    ),
                    fecha_inicio=(
                        item.get("fecha_inicio")
                        or item.get("start_date")
                        or item.get("inicio")
                    ),
                    fecha_fin=(
                        item.get("fecha_fin")
                        or item.get("end_date")
                        or item.get("fin")
                    ),
                    cantidad=(
                        item.get("cantidad")
                        or item.get("quantity")
                        or item.get("cantidad_items")
                    ),
                )
            )

        return normalized
