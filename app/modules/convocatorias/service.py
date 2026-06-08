from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.convocatoria import Convocatoria, ConvocatoriaEstado
from app.modules.convocatorias.repository import ConvocatoriaRepository
from app.modules.convocatorias.schemas.convocatoria import (
    ConvocatoriaCreate,
    ConvocatoriaUpdate,
)
from app.modules.reglas_evaluacion.repository import ReglaEvaluacionRepository

# Default evaluation rules applied to every new convocatoria
DEFAULT_RULES = [
    {
        "tipo_item": "FORMACION",
        "descripcion_regla": "Titulo de doctorado (PhD): 5 pts | maestria: 3 pts | especializacion: 2 pts | pregrado: 1 pt",
        "puntaje_unitario": 3.0,
        "maximo_acumulable": 15.0,
        "unidad": "puntos_por_titulo",
    },
    {
        "tipo_item": "EXPERIENCIA",
        "descripcion_regla": "Cada ano de experiencia docente: 2 pts",
        "puntaje_unitario": 2.0,
        "maximo_acumulable": 20.0,
        "unidad": "puntos_por_ano",
    },
    {
        "tipo_item": "PRODUCCION",
        "descripcion_regla": "Cada publicacion academica o libro: 3 pts",
        "puntaje_unitario": 3.0,
        "maximo_acumulable": 15.0,
        "unidad": "puntos_por_publicacion",
    },
    {
        "tipo_item": "PONENCIA",
        "descripcion_regla": "Cada ponencia en evento academico: 2 pts",
        "puntaje_unitario": 2.0,
        "maximo_acumulable": 10.0,
        "unidad": "puntos_por_ponencia",
    },
    {
        "tipo_item": "INVESTIGACION",
        "descripcion_regla": "Cada proyecto de investigacion: 4 pts",
        "puntaje_unitario": 4.0,
        "maximo_acumulable": 20.0,
        "unidad": "puntos_por_proyecto",
    },
]


def _seed_default_rules(db: object, convocatoria_id: int) -> None:
    """Insert default evaluation rules for a new convocatoria."""
    from app.db.models.hoja_vida import TipoItemHojaVida
    from app.db.models.regla_evaluacion import ReglaEvaluacion

    for rule in DEFAULT_RULES:
        db.add(
            ReglaEvaluacion(
                id_convocatoria=convocatoria_id,
                tipo_item=TipoItemHojaVida[rule["tipo_item"]],
                descripcion_regla=rule["descripcion_regla"],
                puntaje_unitario=rule["puntaje_unitario"],
                maximo_acumulable=rule["maximo_acumulable"],
                unidad=rule["unidad"],
            )
        )


class ConvocatoriaService:
    def __init__(self, repository: ConvocatoriaRepository, db: object | None = None) -> None:
        self.repository = repository
        self.db = db
        self.reglas_repository = (
            ReglaEvaluacionRepository(db) if db is not None else None
        )

    def list_all(self) -> list[Convocatoria]:
        return self.repository.list_all()

    def list_activas(self) -> list[Convocatoria]:
        return self.repository.list_activas()

    def get_active(self) -> Convocatoria | None:
        return self.repository.get_active()

    def get_by_id(self, convocatoria_id: int) -> Convocatoria:
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if convocatoria is None:
            raise NotFoundError("Convocatoria not found")
        return convocatoria

    def create(
        self,
        data: ConvocatoriaCreate,
        creado_por: int,
    ) -> Convocatoria:
        convocatoria = self.repository.create(data, creado_por)
        self.repository.commit()

        # Seed default evaluation rules
        if self.db is not None:
            _seed_default_rules(self.db, convocatoria.id_convocatoria)
            self.repository.commit()

        return convocatoria

    def update(
        self,
        convocatoria_id: int,
        data: ConvocatoriaUpdate,
    ) -> Convocatoria:
        convocatoria = self.get_by_id(convocatoria_id)
        next_fecha_inicio = data.fecha_inicio or convocatoria.fecha_inicio
        next_fecha_cierre = data.fecha_cierre or convocatoria.fecha_cierre
        if next_fecha_cierre < next_fecha_inicio:
            raise ConflictError("fecha_cierre no puede ser anterior a fecha_inicio")
        if convocatoria.estado == ConvocatoriaEstado.CERRADA:
            raise ConflictError("Una convocatoria cerrada no puede modificarse")
        updated = self.repository.update(convocatoria, data)
        self.repository.commit()
        return updated

    def delete(self, convocatoria_id: int) -> None:
        convocatoria = self.get_by_id(convocatoria_id)
        self.repository.delete(convocatoria)
        self.repository.commit()

    def activate(self, convocatoria_id: int) -> Convocatoria:
        convocatoria = self.get_by_id(convocatoria_id)
        if convocatoria.estado == ConvocatoriaEstado.CERRADA:
            raise ConflictError("No se puede activar una convocatoria cerrada")
        if self.reglas_repository is None:
            raise ConflictError("No hay acceso a las reglas de evaluacion")
        reglas = self.reglas_repository.list_by_convocatoria(convocatoria_id)
        if not reglas:
            raise ConflictError("No se puede activar una convocatoria sin reglas")
        self.repository.deactivate_current_active(keep_convocatoria_id=convocatoria_id)
        updated = self.repository.update(
            convocatoria,
            ConvocatoriaUpdate(
                activa=True,
                estado=ConvocatoriaEstado.ACTIVA,
            ),
        )
        self.repository.commit()
        return updated

    def close(self, convocatoria_id: int) -> Convocatoria:
        convocatoria = self.get_by_id(convocatoria_id)
        updated = self.repository.update(
            convocatoria,
            ConvocatoriaUpdate(
                activa=False,
                estado=ConvocatoriaEstado.CERRADA,
            ),
        )
        self.repository.commit()
        return updated
