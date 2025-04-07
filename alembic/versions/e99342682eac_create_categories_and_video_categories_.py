"""create categories and video_categories tables

Revision ID: e99342682eac
Revises: e62047d38040
Create Date: 2024-12-25 17:58:32.659722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e99342682eac'
down_revision: Union[str, None] = 'e62047d38040'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, unique=True, nullable=False),
    )

    # Create video_categories table
    op.create_table(
        'video_categories',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('video_id', sa.Integer, sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
    )

def downgrade():
    # Drop video_categories table first
    op.drop_table('video_categories')
    # Drop categories table
    op.drop_table('categories')
