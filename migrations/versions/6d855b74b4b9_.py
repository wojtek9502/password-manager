"""empty message

Revision ID: 6d855b74b4b9
Revises: e79542361ede
Create Date: 2024-02-18 14:57:33.518447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d855b74b4b9'
down_revision: Union[str, None] = 'e79542361ede'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pa_password_history', sa.Column('password_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'pa_password_history', 'pa_password', ['password_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(None, 'pa_password_history', type_='foreignkey')
    op.drop_column('pa_password_history', 'password_id')
