"""Session is active

Revision ID: 536b5a37d7a8
Revises: d4b5d824c1e5
Create Date: 2024-11-26 18:45:24.574685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '536b5a37d7a8'
down_revision: Union[str, None] = 'd4b5d824c1e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Agregar columna 'is_active' con default=True
    op.add_column('sessions', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()))
    
    # Actualizar todas las sesiones existentes para que 'is_active' sea False
    op.execute('UPDATE sessions SET is_active = FALSE')
    
    # Cambiar el default de la columna a None para futuras migraciones
    op.alter_column('sessions', 'is_active', server_default=None)

def downgrade():
    # Eliminar la columna 'is_active'
    op.drop_column('sessions', 'is_active')