"""Initial migration

Revision ID: 5c4dd0dc2a8b
Revises: 8045822c4b26
Create Date: 2026-02-14 00:47:43.315538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c4dd0dc2a8b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
