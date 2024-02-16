"""empty message

Revision ID: 4ccebb79096b
Revises: 74bac5c2917f
Create Date: 2024-02-08 20:22:59.006120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ccebb79096b'
down_revision: Union[str, None] = '74bac5c2917f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('gr_group',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=4089), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pa_password',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=4089), nullable=False),
    sa.Column('login', sa.String(length=2048), nullable=False),
    sa.Column('password_hash', sa.LargeBinary(length=8192), nullable=False),
    sa.Column('salt', sa.LargeBinary(length=256), nullable=False),
    sa.Column('hash_algo', sa.String(length=30), nullable=False),
    sa.Column('iterations', sa.Integer(), nullable=False),
    sa.Column('note', sa.String(length=8192), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('inserted_on', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['us_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('us_user_group',
    sa.Column('group_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['gr_group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['us_user.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'user_id')
    )

    op.create_table('pa_password_group',
    sa.Column('group_id', sa.UUID(), nullable=False),
    sa.Column('password_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['gr_group.id'], ),
    sa.ForeignKeyConstraint(['password_id'], ['pa_password.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'password_id')
    )

    op.create_table('pa_password_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=4089), nullable=False),
    sa.Column('username', sa.String(length=2048), nullable=False),
    sa.Column('old_password_hash', sa.LargeBinary(length=8192), nullable=False),
    sa.Column('old_salt', sa.LargeBinary(length=256), nullable=False),
    sa.Column('hash_algo', sa.String(length=30), nullable=False),
    sa.Column('iterations', sa.Integer(), nullable=False),
    sa.Column('note', sa.String(length=8192), nullable=True),
    sa.Column('changed_by_user_id', sa.UUID(), nullable=True),
    sa.Column('password_id', sa.UUID(), nullable=True),
    sa.Column('inserted_on', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['changed_by_user_id'], ['us_user.id'], ),
    sa.ForeignKeyConstraint(['password_id'], ['pa_password.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pa_password_url',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('url', sa.String(length=4089), nullable=False),
    sa.Column('password_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['password_id'], ['pa_password.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('pa_password_url')
    op.drop_table('pa_password_history')
    op.drop_table('pa_password_group')
    op.drop_table('us_user_group')
    op.drop_table('pa_password')
    op.drop_table('gr_group')
