"""Add level relation to User

Revision ID: f897123d7ee4
Revises: e99342682eac
Create Date: 2024-12-25 21:48:23.566322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Integer
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f897123d7ee4'
down_revision: Union[str, None] = 'e99342682eac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Agregar columna level_id a la tabla users
    op.add_column('users', sa.Column('level_id', sa.Integer(), sa.ForeignKey('levels.level_id'), nullable=True))
    
    # Crear un índice para la columna level_id (opcional, mejora rendimiento)
    op.create_index('ix_users_level_id', 'users', ['level_id'])
    
    # Tabla temporal para actualizar datos
    user_table = table('users', column('level_id', Integer))
    
    # Asignar el nivel por defecto (id 1) a los usuarios existentes
    op.execute(
        user_table.update().values(level_id=1)
    )
    
    # Establecer la columna como no nula después de asignar el nivel
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('level_id', nullable=False)

def downgrade():
    # Quitar las modificaciones (en caso de rollback)
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('users_level_id_fkey', type_='foreignkey')
        batch_op.drop_column('level_id')
    op.drop_index('ix_users_level_id', table_name='users')