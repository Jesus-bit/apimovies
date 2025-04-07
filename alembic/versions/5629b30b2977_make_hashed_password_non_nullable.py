"""Make hashed_password non-nullable

Revision ID: 5629b30b2977
Revises: 5a670a6dc0bc
Create Date: 2024-11-16 21:24:58.572843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5629b30b2977'
down_revision: Union[str, None] = '5a670a6dc0bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Hacer que hashed_password sea no nulo
    op.alter_column('users', 'hashed_password', nullable=False)

def downgrade():
    # Revertir a nullable
    op.alter_column('users', 'hashed_password', nullable=True)
