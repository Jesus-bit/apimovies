"""create type_transaction with change title

Revision ID: 1f3441ff0ba7
Revises: ba01242da133
Create Date: 2025-01-01 15:29:18.549471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1f3441ff0ba7'
down_revision: Union[str, None] = 'ba01242da133'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Agregar el nuevo valor al tipo Enum
    op.execute("ALTER TYPE transaction_types ADD VALUE 'change title';")

def downgrade():
    # Nota: No se puede eliminar un valor de un Enum en PostgreSQL directamente.
    # Tendrías que recrear el tipo sin el valor adicional.
    pass
