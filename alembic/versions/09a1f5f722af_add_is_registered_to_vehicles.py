"""add is_registered to vehicles

Revision ID: 09a1f5f722af
Revises: 3e5f3361d194
Create Date: 2026-05-19 00:47:46.939381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09a1f5f722af'
down_revision: Union[str, Sequence[str], None] = '3e5f3361d194'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('vehicles', sa.Column('is_registered', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('vehicles', 'is_registered')
