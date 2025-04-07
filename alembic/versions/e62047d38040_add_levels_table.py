"""add_levels_table

Revision ID: e62047d38040
Revises: 171df89ee8bd
Create Date: 2024-12-24 17:58:36.766772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e62047d38040'
down_revision: Union[str, None] = '171df89ee8bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'levels',
        sa.Column('level_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('required_points', sa.Integer, nullable=False),
        sa.Column('medal_url', sa.String(length=255), nullable=False),
    )


def downgrade():
    op.drop_table('levels')