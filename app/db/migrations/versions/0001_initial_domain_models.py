"""initial domain models

Revision ID: 0001_initial_domain_models
Revises:
Create Date: 2026-05-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_domain_models"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


user_role = postgresql.ENUM("ASPIRANTE", "ADMIN", name="user_role", create_type=False)
postulacion_estado = postgresql.ENUM(
    "BORRADOR",
    "ENVIADA",
    "EN_EVALUACION",
    "EVALUADA",
    "RECHAZADA",
    name="postulacion_estado",
    create_type=False,
)
tipo_item_hoja_vida = postgresql.ENUM(
    "FORMACION",
    "EXPERIENCIA",
    "PRODUCCION",
    "DOCUMENTO",
    "OTRO",
    name="tipo_item_hoja_vida",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    postulacion_estado.create(bind, checkfirst=True)
    tipo_item_hoja_vida.create(bind, checkfirst=True)

    op.create_table(
        "usuario",
        sa.Column("id_usuario", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("apellido", sa.String(length=120), nullable=False),
        sa.Column("cedula", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("telefono", sa.String(length=40), nullable=True),
        sa.Column("municipio", sa.String(length=120), nullable=True),
        sa.Column("departamento", sa.String(length=120), nullable=True),
        sa.Column("pais", sa.String(length=120), nullable=True, server_default="Colombia"),
        sa.Column("rol", user_role, nullable=False, server_default="ASPIRANTE"),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "fecha_registro",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "fecha_actualizacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_usuarios_id_usuario", "usuario", ["id_usuario"])
    op.create_index("ix_usuarios_cedula", "usuario", ["cedula"], unique=True)
    op.create_index("ix_usuarios_email", "usuario", ["email"], unique=True)

    op.create_table(
        "convocatoria",
        sa.Column("id_convocatoria", sa.Integer(), primary_key=True),
        sa.Column("titulo", sa.String(length=180), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_cierre", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("creado_por", sa.Integer(), nullable=False),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "fecha_actualizacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["creado_por"], ["usuario.id_usuario"]),
    )
    op.create_index("ix_convocatorias_id_convocatoria", "convocatoria", ["id_convocatoria"])

    op.create_table(
        "postulaciones",
        sa.Column("id_postulacion", sa.Integer(), primary_key=True),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("id_convocatoria", sa.Integer(), nullable=False),
        sa.Column("estado", postulacion_estado, nullable=False, server_default="BORRADOR"),
        sa.Column("puntaje_total", sa.Numeric(8, 2), nullable=True),
        sa.Column("url_cv_original", sa.String(length=500), nullable=True),
        sa.Column("observaciones_admin", sa.Text(), nullable=True),
        sa.Column("fecha_envio", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_evaluacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "fecha_actualizacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id_usuario"]),
        sa.ForeignKeyConstraint(["id_convocatoria"], ["convocatorias.id_convocatoria"]),
        sa.UniqueConstraint(
            "id_usuario",
            "id_convocatoria",
            name="uq_postulacion_usuario_convocatoria",
        ),
    )
    op.create_index("ix_postulaciones_id_postulacion", "postulaciones", ["id_postulacion"])
    op.create_index("ix_postulaciones_id_usuario", "postulaciones", ["id_usuario"])
    op.create_index("ix_postulaciones_id_convocatoria", "postulaciones", ["id_convocatoria"])

    op.create_table(
        "items_hoja_vida",
        sa.Column("id_item", sa.Integer(), primary_key=True),
        sa.Column("id_postulacion", sa.Integer(), nullable=False),
        sa.Column("tipo_item", tipo_item_hoja_vida, nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("institucion", sa.String(length=180), nullable=True),
        sa.Column("fecha_inicio", sa.Date(), nullable=True),
        sa.Column("fecha_fin", sa.Date(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=True),
        sa.Column("puntaje_asignado", sa.Numeric(8, 2), nullable=True),
        sa.Column("validado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["id_postulacion"], ["postulaciones.id_postulacion"]),
    )
    op.create_index("ix_items_hoja_vida_id_item", "items_hoja_vida", ["id_item"])
    op.create_index("ix_items_hoja_vida_id_postulacion", "items_hoja_vida", ["id_postulacion"])

    op.create_table(
        "soportes_item",
        sa.Column("id_soporte", sa.Integer(), primary_key=True),
        sa.Column("id_item", sa.Integer(), nullable=False),
        sa.Column("nombre_archivo", sa.String(length=255), nullable=False),
        sa.Column("url_archivo", sa.String(length=500), nullable=False),
        sa.Column("tipo_archivo", sa.String(length=120), nullable=False),
        sa.Column("tamanio_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "fecha_carga",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["id_item"], ["items_hoja_vida.id_item"]),
    )
    op.create_index("ix_soportes_item_id_soporte", "soportes_item", ["id_soporte"])
    op.create_index("ix_soportes_item_id_item", "soportes_item", ["id_item"])

    op.create_table(
        "reglas_evaluacion",
        sa.Column("id_regla", sa.Integer(), primary_key=True),
        sa.Column("id_convocatoria", sa.Integer(), nullable=False),
        sa.Column("tipo_item", tipo_item_hoja_vida, nullable=False),
        sa.Column("descripcion_regla", sa.Text(), nullable=False),
        sa.Column("puntaje_unitario", sa.Numeric(8, 2), nullable=False),
        sa.Column("maximo_acumulable", sa.Numeric(8, 2), nullable=True),
        sa.Column("unidad", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["id_convocatoria"], ["convocatoria.id_convocatoria"]),
    )
    op.create_index("ix_reglas_evaluacion_id_regla", "reglas_evaluacion", ["id_regla"])
    op.create_index("ix_reglas_evaluacion_id_convocatoria", "reglas_evaluacion", ["id_convocatoria"])


def downgrade() -> None:
    op.drop_index("ix_reglas_evaluacion_id_convocatoria", table_name="reglas_evaluacion")
    op.drop_index("ix_reglas_evaluacion_id_regla", table_name="reglas_evaluacion")
    op.drop_table("reglas_evaluacion")

    op.drop_index("ix_soportes_item_id_item", table_name="soportes_item")
    op.drop_index("ix_soportes_item_id_soporte", table_name="soportes_item")
    op.drop_table("soportes_item")

    op.drop_index("ix_items_hoja_vida_id_postulacion", table_name="items_hoja_vida")
    op.drop_index("ix_items_hoja_vida_id_item", table_name="items_hoja_vida")
    op.drop_table("items_hoja_vida")

    op.drop_index("ix_postulaciones_id_convocatoria", table_name="postulaciones")
    op.drop_index("ix_postulaciones_id_usuario", table_name="postulaciones")
    op.drop_index("ix_postulaciones_id_postulacion", table_name="postulaciones")
    op.drop_table("postulaciones")

    op.drop_index("ix_convocatorias_id_convocatoria", table_name="convocatoria")
    op.drop_table("convocatoria")

    op.drop_index("ix_usuarios_email", table_name="usuario")
    op.drop_index("ix_usuarios_cedula", table_name="usuario")
    op.drop_index("ix_usuarios_id_usuario", table_name="usuario")
    op.drop_table("usuario")

    bind = op.get_bind()
    tipo_item_hoja_vida.drop(bind, checkfirst=True)
    postulacion_estado.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
