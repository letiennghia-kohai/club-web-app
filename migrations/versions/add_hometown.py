"""
Migration to add hometown field to users table
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add hometown column
    op.add_column('users', sa.Column('hometown', sa.String(length=100), nullable=True))
    print('✓ Added hometown column to users table')


def downgrade():
    op.drop_column('users', 'hometown')
