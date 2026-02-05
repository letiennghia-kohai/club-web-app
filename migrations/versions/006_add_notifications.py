"""Add notification system

Revision ID: 006_add_notifications
Revises: 005_add_avatar
Create Date: 2026-02-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_notifications'
down_revision = '005_add_avatar'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification table
    op.create_table('notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('ADMIN_POST', 'POST_COMMENT', name='notificationtype'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_notification_user_id'), 'notification', ['user_id'], unique=False)
    op.create_index(op.f('ix_notification_is_read'), 'notification', ['is_read'], unique=False)
    op.create_index(op.f('ix_notification_created_at'), 'notification', ['created_at'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_notification_created_at'), table_name='notification')
    op.drop_index(op.f('ix_notification_is_read'), table_name='notification')
    op.drop_index(op.f('ix_notification_user_id'), table_name='notification')
    
    # Drop table
    op.drop_table('notification')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS notificationtype')
