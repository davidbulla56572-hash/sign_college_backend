from datetime import date
from types import SimpleNamespace

from app.db.models.hoja_vida import TipoItemHojaVida
from app.db.models.postulacion import PostulacionEstado
from app.modules.cv_processing.normalization import CVNormalizationService
from app.modules.cv_processing.service import HojaVidaService


class _RepoStub:
    def get_draft_hoja_vida(self, user_id: int, postulacion_id: int):
        return {
            "postulacion": SimpleNamespace(
                id_postulacion=postulacion_id,
                id_convocatoria=7,
                estado=PostulacionEstado.BORRADOR,
                url_cv_original="uploads/cv/test.pdf",
            ),
            "convocatoria": SimpleNamespace(titulo="Convocatoria Docente"),
            "items": [
                SimpleNamespace(
                    tipo_item=TipoItemHojaVida.FORMACION,
                    descripcion="Maestria en Educacion",
                    institucion="Universidad Nacional",
                    fecha_inicio=date(2020, 1, 1),
                    fecha_fin=date(2022, 12, 31),
                    cantidad=1,
                ),
                SimpleNamespace(
                    tipo_item=TipoItemHojaVida.EXPERIENCIA,
                    descripcion="Docente de planta",
                    institucion="Colegio Central",
                    fecha_inicio=date(2023, 1, 1),
                    fecha_fin=None,
                    cantidad=1,
                ),
            ],
        }


class _UnusedDependency:
    pass


def test_get_draft_hoja_vida_returns_serializable_items() -> None:
    service = HojaVidaService(
        repository=_RepoStub(),
        extraction_provider=_UnusedDependency(),
        storage=_UnusedDependency(),
        normalizer=CVNormalizationService(),
    )

    user = SimpleNamespace(
        id_usuario=2,
        nombre="Ana",
        apellido="Perez",
        email="ana@example.com",
        telefono="3000000000",
        municipio="Bogota",
        departamento="Cundinamarca",
        pais="Colombia",
    )

    draft = service.get_draft_hoja_vida(user, postulacion_id=15)

    assert draft is not None
    assert draft.items.formacion[0].descripcion == "Maestria en Educacion"
    assert draft.items.formacion[0].institucion == "Universidad Nacional"
    assert draft.items.formacion[0].fecha_inicio == date(2020, 1, 1)
    assert draft.items.experiencia[0].descripcion == "Docente de planta"
    assert draft.items.experiencia[0].fecha_fin is None
