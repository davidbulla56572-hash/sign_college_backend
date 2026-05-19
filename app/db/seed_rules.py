"""Seed default evaluation rules for convocatorias that don't have any."""

from app.db.session import SessionLocal
from app.db.models.convocatoria import Convocatoria
from app.db.models.hoja_vida import TipoItemHojaVida
from app.db.models.regla_evaluacion import ReglaEvaluacion
from sqlalchemy import select

DEFAULT_RULES = [
    ("FORMACION", "Titulo de doctorado (PhD): 5 pts | maestria: 3 pts | especializacion: 2 pts | pregrado: 1 pt", 3.0, 15.0, "puntos_por_titulo"),
    ("EXPERIENCIA", "Cada ano de experiencia docente: 2 pts", 2.0, 20.0, "puntos_por_ano"),
    ("PRODUCCION", "Cada publicacion academica o libro: 3 pts", 3.0, 15.0, "puntos_por_publicacion"),
    ("PONENCIA", "Cada ponencia en evento academico: 2 pts", 2.0, 10.0, "puntos_por_ponencia"),
    ("INVESTIGACION", "Cada proyecto de investigacion: 4 pts", 4.0, 20.0, "puntos_por_proyecto"),
]


def seed_rules_for_existing_convocatorias() -> None:
    db = SessionLocal()
    try:
        convocatorias = list(db.scalars(select(Convocatoria)).all())
        print(f"Found {len(convocatorias)} convocatoria(s)")

        for conv in convocatorias:
            existing_rules = list(
                db.scalars(
                    select(ReglaEvaluacion).where(
                        ReglaEvaluacion.id_convocatoria == conv.id_convocatoria
                    )
                ).all()
            )

            if existing_rules:
                print(f"  Convocatoria '{conv.titulo}' (id={conv.id_convocatoria}): "
                      f"ya tiene {len(existing_rules)} reglas. Skipping.")
                continue

            print(f"  Convocatoria '{conv.titulo}' (id={conv.id_convocatoria}): "
                  f"agregando {len(DEFAULT_RULES)} reglas por defecto...")

            for tipo_str, desc, puntaje, maximo, unidad in DEFAULT_RULES:
                db.add(
                    ReglaEvaluacion(
                        id_convocatoria=conv.id_convocatoria,
                        tipo_item=TipoItemHojaVida[tipo_str],
                        descripcion_regla=desc,
                        puntaje_unitario=puntaje,
                        maximo_acumulable=maximo,
                        unidad=unidad,
                    )
                )

            db.commit()
            print(f"    -> Done!")

    except Exception as exc:
        db.rollback()
        print(f"Error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_rules_for_existing_convocatorias()
