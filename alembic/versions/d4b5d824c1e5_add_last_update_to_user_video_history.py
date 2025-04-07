"""Add last_update to user_video_history

Revision ID: d4b5d824c1e5
Revises: 5629b30b2977
Create Date: 2024-11-23 12:02:54.073567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4b5d824c1e5'
down_revision: Union[str, None] = '5629b30b2977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.add_column('user_video_history', 
        sa.Column('last_update', sa.DateTime(), 
                  server_default=sa.func.now(), 
                  onupdate=sa.func.now())
    )


def downgrade():
    op.drop_column('user_video_history', 'last_update')