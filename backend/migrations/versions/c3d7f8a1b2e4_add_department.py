"""add department model

Revision ID: c3d7f8a1b2e4
Revises: 8bacff9a0333
Create Date: 2026-06-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d7f8a1b2e4'
down_revision = '8bacff9a0333'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('department_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_users_department_id', 'departments', ['department_id'], ['id']
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_department_id', type_='foreignkey')
        batch_op.drop_column('department_id')
    op.drop_table('departments')
