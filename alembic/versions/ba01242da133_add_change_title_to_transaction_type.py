"""add change_title to transaction_type

Revision ID: ba01242da133
Revises: 91f982d5af9f
Create Date: 2025-01-01 15:19:07.506556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ba01242da133'
down_revision: Union[str, None] = '91f982d5af9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Crear el tipo Enum globalmente en la base de datos
    transaction_type_enum = sa.Enum(
        "buy erizo",
        "login",
        "watch video views",
        "watch video no views",
        "rating video",
        "give like",
        "add actor video",
        "vote",
        name="transaction_types"
    )
    transaction_type_enum.create(op.get_bind(), checkfirst=True)

    # Modificar la columna para usar este tipo global
    op.alter_column(
        'transactions',
        'transaction_type',
        type_=transaction_type_enum,
        existing_type=sa.Enum(
            "buy erizo",
            "login",
            "watch video views",
            "watch video no views",
            "rating video",
            "give like",
            "add actor video",
            "vote"
        ),
    )


def downgrade():
    # Revertir la columna a un tipo local (si fuera necesario)
    local_transaction_type_enum = sa.Enum(
        "buy erizo",
        "login",
        "watch video views",
        "watch video no views",
        "rating video",
        "give like",
        "add actor video",
        "vote"
    )
    op.alter_column(
        'transactions',
        'transaction_type',
        type_=local_transaction_type_enum,
        existing_type=sa.Enum(
            "buy erizo",
            "login",
            "watch video views",
            "watch video no views",
            "rating video",
            "give like",
            "add actor video",
            "vote",
            name="transaction_types"
        ),
    )

    # Eliminar el tipo Enum global de la base de datos
    transaction_type_enum = sa.Enum(
        "buy erizo",
        "login",
        "watch video views",
        "watch video no views",
        "rating video",
        "give like",
        "add actor video",
        "vote",
        name="transaction_types"
    )
    transaction_type_enum.drop(op.get_bind(), checkfirst=True)
