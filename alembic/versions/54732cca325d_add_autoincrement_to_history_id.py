"""Add autoincrement to history_id

Revision ID: 54732cca325d
Revises: 536b5a37d7a8
Create Date: 2024-11-30 22:56:22.746634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '54732cca325d'
down_revision: Union[str, None] = '536b5a37d7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Modifica la columna history_id para agregar autoincremento
    op.alter_column('user_video_history', 
                    'history_id',
                    type_=sa.Integer(),
                    autoincrement=True,
                    existing_nullable=False,
                    existing_primary_key=True)


def downgrade() -> None:
    # Opción de rollback si es necesario
    op.alter_column('user_video_history', 
                    'history_id',
                    type_=sa.Integer(),
                    autoincrement=False,
                    existing_nullable=False,
                    existing_primary_key=True)