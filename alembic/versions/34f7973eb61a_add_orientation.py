"""add_orientation

Revision ID: 34f7973eb61a
Revises: bb281ba2cb9a
Create Date: 2024-11-10 18:42:15.406078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '34f7973eb61a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar la columna
    op.drop_column('videos', 'orientation')
    
    # Eliminar el tipo enum
    op.execute('DROP TYPE orientationtype')


def downgrade() -> None:
    return