"""rename category to category_name

Revision ID: 14cdd7103e00
Revises: 1f3441ff0ba7
Create Date: 2025-03-08 20:30:45.679202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '14cdd7103e00'
down_revision: Union[str, None] = '1f3441ff0ba7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Renombrar la columna "category" a "category_name"
    op.alter_column('videos', 'category', new_column_name='category_name')

def downgrade():
    # Revertir el cambio si es necesario
    op.alter_column('videos', 'category_name', new_column_name='category')
