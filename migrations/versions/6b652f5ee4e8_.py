"""empty message

Revision ID: 6b652f5ee4e8
Revises: dae66c1c6bdc
Create Date: 2024-02-21 15:45:08.524215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b652f5ee4e8'
down_revision: Union[str, None] = 'dae66c1c6bdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('us_user', sa.Column('password_crypto', sa.LargeBinary(length=8192), nullable=False))


def downgrade() -> None:
    op.drop_column('us_user', 'password_crypto')
