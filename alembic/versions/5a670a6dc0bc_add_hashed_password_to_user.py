"""Add hashed_password to User

Revision ID: 5a670a6dc0bc
Revises: 0dc29e63cc87
Create Date: 2024-11-16 20:34:39.231067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5a670a6dc0bc'
down_revision: Union[str, None] = '0dc29e63cc87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Añadir la columna hashed_password
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))

def downgrade():
    # Eliminar la columna hashed_password
    op.drop_column('users', 'hashed_password')