"""Add users, erizos, and transactions tables

Revision ID: 91f982d5af9f
Revises: ffc25b31bde7
Create Date: 2024-12-31 15:12:52.702989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '91f982d5af9f'
down_revision: Union[str, None] = 'ffc25b31bde7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def type_exists(conn, type_name):
    query = f"SELECT 1 FROM pg_type WHERE typname = '{type_name}'"
    return conn.execute(sa.text(query)).scalar() is not None

def upgrade():
    # Create ENUM types if not exists
    conn = op.get_bind()

    if not type_exists(conn, 'erizo_states'):
        print("pasa la prueba pero no lo hace")
        # erizo_states_enum = sa.Enum('active', 'used', name='erizo_states')
        # erizo_states_enum.create(op.get_bind())

    if not type_exists(conn, 'transaction_types'):
        # transaction_types_enum = sa.Enum(
        #     "buy erizo",
        #     "login",
        #     "watch video views",
        #     "watch video no views",
        #     "rating video",
        #     "give like",
        #     "add actor video",
        #     "vote",
        #     name='transaction_types'
        # )
        # transaction_types_enum.create(op.get_bind())
        print("paso transaccions")
    if not type_exists(conn, 'movement_types'):
        print("paso los movement")
        # movement_types_enum = sa.Enum('in', 'out', name='movement_types', create_type=False)
        # movement_types_enum.create(op.get_bind())

    # Create erizos table
    op.create_table(
        'erizos',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('state', sa.Enum('active', 'used', name='erizo_states', create_type=False)),
        sa.Column('date_acquisition', sa.DateTime, default=sa.func.now()),
    )

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('transaction_type', sa.Enum(
            "buy erizo",
            "login",
            "watch video views",
            "watch video no views",
            "rating video",
            "give like",
            "add actor video",
            "vote",
            name='transaction_types',
            create_type=False
        )),
        sa.Column('coins_amount', sa.Float),
        sa.Column('movement_type', sa.Enum('in', 'out', name='movement_types', create_type=False)),
        sa.Column('date', sa.DateTime, default=sa.func.now()),
    )

def downgrade():
    # Drop tables
    op.drop_table('transactions')
    op.drop_table('erizos')
    op.drop_table('users')

    # Drop ENUM types
    movement_types_enum = sa.Enum('in', 'out', name='movement_types')
    transaction_types_enum = sa.Enum(
        'buy erizo', 'hacer login', 'watch video', 'rating video', 'give like', 'add actor video',
        name='transaction_types'
    )
    erizo_states_enum = sa.Enum('active', 'used', name='erizo_states')

    movement_types_enum.drop(op.get_bind())
    transaction_types_enum.drop(op.get_bind())
    erizo_states_enum.drop(op.get_bind())