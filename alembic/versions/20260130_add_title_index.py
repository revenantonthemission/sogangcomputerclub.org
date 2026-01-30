"""add_index_to_memos_title

Revision ID: 20260130_add_title_index
Revises: d7d5dc8a9fe3
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260130_add_title_index'
down_revision: Union[str, None] = 'd7d5dc8a9fe3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add index on memos.title column for faster search queries."""
    op.create_index('ix_memos_title', 'memos', ['title'], unique=False)


def downgrade() -> None:
    """Remove the title index."""
    op.drop_index('ix_memos_title', table_name='memos')
