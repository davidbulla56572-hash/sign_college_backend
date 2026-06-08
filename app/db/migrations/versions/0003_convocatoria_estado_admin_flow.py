"""add convocatoria estado for admin flow

Revision ID: 0003_convocatoria_admin
Revises: 0002_extend_hoja_vida_item_types
Create Date: 2026-06-08
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003_convocatoria_admin"
down_revision: str | None = "0002_extend_hoja_vida_item_types"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


convocatoria_estado = postgresql.ENUM(
    "BORRADOR",
    "ACTIVA",
    "CERRADA",
    name="convocatoria_estado",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    convocatoria_estado.create(bind, checkfirst=True)

    op.add_column(
        "convocatoria",
        sa.Column(
            "estado",
            convocatoria_estado,
            nullable=False,
            server_default="BORRADOR",
        ),
    )
    op.execute(
        """
        UPDATE convocatoria
        SET estado = CASE
            WHEN activa = true THEN 'ACTIVA'::convocatoria_estado
            ELSE 'BORRADOR'::convocatoria_estado
        END
        """
    )
    op.alter_column("convocatoria", "estado", server_default=None)

    op.execute("UPDATE convocatoria SET activa = false WHERE estado <> 'ACTIVA'")


def downgrade() -> None:
    op.drop_column("convocatoria", "estado")

    bind = op.get_bind()
    convocatoria_estado.drop(bind, checkfirst=True)
