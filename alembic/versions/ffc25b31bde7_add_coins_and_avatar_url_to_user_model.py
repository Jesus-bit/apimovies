"""Add coins and avatar_url to User model

Revision ID: ffc25b31bde7
Revises: f897123d7ee4
Create Date: 2024-12-25 22:20:27.699077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ffc25b31bde7'
down_revision: Union[str, None] = 'f897123d7ee4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Agregar las nuevas columnas a la tabla `users`
    op.add_column('users', sa.Column('coins', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))

def downgrade():
    # Eliminar las columnas en caso de rollback
    op.drop_column('users', 'coins')
    op.drop_column('users', 'avatar_url')