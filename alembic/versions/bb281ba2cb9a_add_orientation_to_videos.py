"""add_orientation_to_videos

Revision ID: bb281ba2cb9a
Revises: d9b2029ee54d
Create Date: 2024-11-10 18:07:18.516496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bb281ba2cb9a'
down_revision: Union[str, None] = '34f7973eb61a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear el tipo enum con los valores en mayúsculas
    orientation_type = postgresql.ENUM('HORIZONTAL', 'VERTICAL', name='orientationtype')
    orientation_type.create(op.get_bind())

    # Agregar la columna orientation
    op.add_column('videos', sa.Column('orientation', sa.Enum('HORIZONTAL', 'VERTICAL', name='orientationtype'), 
                                      nullable=False, 
                                      server_default='HORIZONTAL'))

    # Actualizar orientación basado en la ruta de video_url
    op.execute("""
    UPDATE videos 
    SET orientation = CASE 
        WHEN video_url LIKE '%%/videos/horizontales/%%' THEN 'HORIZONTAL'::orientationtype
        WHEN video_url LIKE '%%/videos/verticales/%%' THEN 'VERTICAL'::orientationtype
        ELSE 'HORIZONTAL'::orientationtype  -- Valor predeterminado en caso de otras rutas
    END
    """)


def downgrade() -> None:
    # Eliminar la columna
    op.drop_column('videos', 'orientation')
    
    # Eliminar el tipo enum
    op.execute('DROP TYPE orientationtype')
