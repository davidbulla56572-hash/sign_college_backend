"""extend hoja vida item types

Revision ID: 0002_extend_hoja_vida_item_types
Revises: 0001_initial_domain_models
Create Date: 2026-05-19
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_extend_hoja_vida_item_types"
down_revision: str | None = "0001_initial_domain_models"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE tipo_item_hoja_vida ADD VALUE IF NOT EXISTS 'PONENCIA'")
    op.execute("ALTER TYPE tipo_item_hoja_vida ADD VALUE IF NOT EXISTS 'INVESTIGACION'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values safely without type recreation.
    pass
