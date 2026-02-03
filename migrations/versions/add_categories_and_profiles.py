"""Add category model and user profile enhancements

Revision ID: add_categories_and_profiles
Revises: 
Create Date: 2026-02-03 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_categories_and_profiles'
down_revision = None  # Update this if you have previous migrations
branch_labels = None
depends_on = None


def upgrade():
    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    
    # Add category_id to posts
    op.add_column('posts', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_posts_category_id'), 'posts', ['category_id'], unique=False)
    op.create_foreign_key('fk_posts_category', 'posts', 'categories', ['category_id'], ['id'])
    
    # Add new fields to users table
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(length=15), nullable=True))
    op.add_column('users', sa.Column('facebook_link', sa.String(length=255), nullable=True))
    
    # Insert default categories
    op.execute("""
        INSERT INTO categories (name, slug, description, "order", created_at, updated_at)
        VALUES 
            ('Tin tức & Hoạt động', 'tin-tuc-hoat-dong', 'Tin tức và các hoạt động của câu lạc bộ', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Confession', 'confession', 'Nơi chia sẻ tâm tư, cảm nghĩ của các thành viên', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Thông báo', 'thong-bao', 'Các thông báo quan trọng từ ban quản lý', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Sự kiện', 'su-kien', 'Thông tin về các sự kiện sắp diễn ra', 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """)


def downgrade():
    # Remove new user fields
    op.drop_column('users', 'facebook_link')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'date_of_birth')
    
    # Remove category_id from posts
    op.drop_constraint('fk_posts_category', 'posts', type_='foreignkey')
    op.drop_index(op.f('ix_posts_category_id'), table_name='posts')
    op.drop_column('posts', 'category_id')
    
    # Drop categories table
    op.drop_table('categories')
