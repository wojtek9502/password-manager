"""empty message

Revision ID: 833368c3ee48
Revises: 4ccebb79096b
Create Date: 2024-02-17 22:35:30.636696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '833368c3ee48'
down_revision: Union[str, None] = '4ccebb79096b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pa_password', sa.Column('password_encrypted', sa.LargeBinary(length=8192), nullable=False))
    op.add_column('pa_password', sa.Column('server_side_algo', sa.String(length=30), nullable=False))
    op.add_column('pa_password', sa.Column('server_side_iterations', sa.Integer(), nullable=False))
    op.add_column('pa_password', sa.Column('client_side_algo', sa.String(length=30), nullable=False))
    op.add_column('pa_password', sa.Column('client_side_iterations', sa.Integer(), nullable=False))
    op.drop_column('pa_password', 'hash_algo')
    op.drop_column('pa_password', 'salt')
    op.drop_column('pa_password', 'password_hash')
    op.drop_column('pa_password', 'iterations')
    op.add_column('pa_password_history', sa.Column('login', sa.String(length=2048), nullable=False))
    op.add_column('pa_password_history', sa.Column('password', sa.String(length=8192), nullable=False))
    op.drop_constraint('pa_password_history_changed_by_user_id_fkey', 'pa_password_history', type_='foreignkey')
    op.drop_column('pa_password_history', 'hash_algo')
    op.drop_column('pa_password_history', 'iterations')
    op.drop_column('pa_password_history', 'old_salt')
    op.drop_column('pa_password_history', 'changed_by_user_id')
    op.drop_column('pa_password_history', 'username')
    op.drop_column('pa_password_history', 'old_password_hash')


def downgrade() -> None:
    op.add_column('pa_password_history', sa.Column('old_password_hash', postgresql.BYTEA(), autoincrement=False, nullable=False))
    op.add_column('pa_password_history', sa.Column('username', sa.VARCHAR(length=2048), autoincrement=False, nullable=False))
    op.add_column('pa_password_history', sa.Column('changed_by_user_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('pa_password_history', sa.Column('old_salt', postgresql.BYTEA(), autoincrement=False, nullable=False))
    op.add_column('pa_password_history', sa.Column('iterations', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('pa_password_history', sa.Column('hash_algo', sa.VARCHAR(length=30), autoincrement=False, nullable=False))
    op.create_foreign_key('pa_password_history_changed_by_user_id_fkey', 'pa_password_history', 'us_user', ['changed_by_user_id'], ['id'])
    op.drop_column('pa_password_history', 'password')
    op.drop_column('pa_password_history', 'login')
    op.add_column('pa_password', sa.Column('iterations', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('pa_password', sa.Column('password_hash', postgresql.BYTEA(), autoincrement=False, nullable=False))
    op.add_column('pa_password', sa.Column('salt', postgresql.BYTEA(), autoincrement=False, nullable=False))
    op.add_column('pa_password', sa.Column('hash_algo', sa.VARCHAR(length=30), autoincrement=False, nullable=False))
    op.drop_column('pa_password', 'client_side_iterations')
    op.drop_column('pa_password', 'client_side_algo')
    op.drop_column('pa_password', 'server_side_iterations')
    op.drop_column('pa_password', 'server_side_algo')
    op.drop_column('pa_password', 'password_encrypted')