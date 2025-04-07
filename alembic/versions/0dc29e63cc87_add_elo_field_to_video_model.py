"""Add elo field to Video model

Revision ID: 0dc29e63cc87
Revises: bb281ba2cb9a
Create Date: 2024-11-12 22:31:23.935180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0dc29e63cc87'
down_revision: Union[str, None] = 'bb281ba2cb9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('videos', sa.Column('elo', sa.Integer, nullable=False, server_default='1500'))

def downgrade():
    op.drop_column('videos', 'elo')