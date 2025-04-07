"""add video_chunks table

Revision ID: b338a0fef9ce
Revises: 14cdd7103e00
Create Date: 2025-03-21 15:25:15.198948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b338a0fef9ce'
down_revision: Union[str, None] = '14cdd7103e00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'video_chunks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('video_id', sa.Integer, sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('chunk_start_time', sa.Integer),
        sa.Column('chunk_end_time', sa.Integer)
    )

def downgrade():
    op.drop_table('video_chunks')