"""Add avatar column to users

Revision ID: 005_add_avatar
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add avatar column to users table
    op.add_column('users', sa.Column('avatar', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('users', 'avatar')
