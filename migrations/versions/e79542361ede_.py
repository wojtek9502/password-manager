"""empty message

Revision ID: e79542361ede
Revises: 833368c3ee48
Create Date: 2024-02-18 14:25:08.576569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e79542361ede'
down_revision: Union[str, None] = '833368c3ee48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pa_password_history', sa.Column('password_encrypted', sa.LargeBinary(length=8192), nullable=False))
    op.add_column('pa_password_history', sa.Column('server_side_algo', sa.String(length=30), nullable=False))
    op.add_column('pa_password_history', sa.Column('server_side_iterations', sa.Integer(), nullable=False))
    op.add_column('pa_password_history', sa.Column('client_side_algo', sa.String(length=30), nullable=False))
    op.add_column('pa_password_history', sa.Column('client_side_iterations', sa.Integer(), nullable=False))
    op.add_column('pa_password_history', sa.Column('user_id', sa.UUID(), nullable=True))
    op.alter_column('pa_password_history', 'note',
               existing_type=sa.VARCHAR(length=8192),
               nullable=False)
    op.drop_constraint('pa_password_history_password_id_fkey', 'pa_password_history', type_='foreignkey')
    op.create_foreign_key(None, 'pa_password_history', 'us_user', ['user_id'], ['id'])
    op.drop_column('pa_password_history', 'password')
    op.drop_column('pa_password_history', 'password_id')


def downgrade() -> None:
    op.add_column('pa_password_history', sa.Column('password_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('pa_password_history', sa.Column('password', sa.VARCHAR(length=8192), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'pa_password_history', type_='foreignkey')
    op.create_foreign_key('pa_password_history_password_id_fkey', 'pa_password_history', 'pa_password', ['password_id'], ['id'])
    op.alter_column('pa_password_history', 'note',
               existing_type=sa.VARCHAR(length=8192),
               nullable=True)
    op.drop_column('pa_password_history', 'user_id')
    op.drop_column('pa_password_history', 'client_side_iterations')
    op.drop_column('pa_password_history', 'client_side_algo')
    op.drop_column('pa_password_history', 'server_side_iterations')
    op.drop_column('pa_password_history', 'server_side_algo')
    op.drop_column('pa_password_history', 'password_encrypted')
