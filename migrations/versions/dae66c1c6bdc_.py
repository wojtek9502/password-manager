"""empty message

Revision ID: dae66c1c6bdc
Revises: 6d855b74b4b9
Create Date: 2024-02-20 17:02:22.438608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dae66c1c6bdc'
down_revision: Union[str, None] = '6d855b74b4b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pa_password_history', sa.Column('client_side_password_encrypted', sa.LargeBinary(length=8192), nullable=False))
    op.drop_column('pa_password_history', 'server_side_iterations')
    op.drop_column('pa_password_history', 'server_side_algo')
    op.drop_column('pa_password_history', 'password_encrypted')


def downgrade() -> None:
    op.add_column('pa_password_history', sa.Column('password_encrypted', postgresql.BYTEA(), autoincrement=False, nullable=False))
    op.add_column('pa_password_history', sa.Column('server_side_algo', sa.VARCHAR(length=30), autoincrement=False, nullable=False))
    op.add_column('pa_password_history', sa.Column('server_side_iterations', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('pa_password_history', 'client_side_password_encrypted')