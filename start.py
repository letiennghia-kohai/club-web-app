#!/usr/bin/env python
"""Startup script for Railway deployment"""
import os
import subprocess
import sys

print("=== Starting Railway Deployment ===")

# Initialize database if needed
print("Checking database...")
try:
    from app import create_app, db
    from app.models.user import User, UserRole, UserStatus
    from app.models.post import Post, PostStatus
    from app.models.tag import Tag
    from datetime import datetime, date
    from werkzeug.security import generate_password_hash
    
    app = create_app()
    with app.app_context():
        # Check if database reset is requested
        reset_db = os.environ.get('RESET_DB', '').lower() == 'true'
        
        if reset_db:
            print("🗑️  RESET_DB=true - Resetting database...")
            db.drop_all()
            db.create_all()
            print("✅ Database schema reset")
            
            # Create admin
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role=UserRole.ADMIN,
                full_name='Quản Trị Viên',
                email='admin@karatebk.com',
                status=UserStatus.ACTIVE,
                belt='Đai đen tứ đẳng',
                join_date=date(2020, 1, 1)
            )
            db.session.add(admin)
            
            # Create member
            member = User(
                username='member1',
                password_hash=generate_password_hash('member123'),
                role=UserRole.MEMBER,
                full_name='Nguyễn Văn A',
                email='member1@example.com',
                student_id='20200001',
                status=UserStatus.ACTIVE,
                belt='Kuy 5',
                join_date=date(2023, 9, 1)
            )
            db.session.add(member)
            db.session.commit()
            
            # Create tags
            tags = []
            for name, slug, color in [
                ('Thông báo', 'thong-bao', '#3b82f6'),
                ('Sự kiện', 'su-kien', '#10b981'),
                ('Thi đấu', 'thi-dau', '#f59e0b'),
                ('Tuyển sinh', 'tuyen-sinh', '#8b5cf6'),
                ('Confession', 'confession', '#ec4899'),
            ]:
                tag = Tag(name=name, slug=slug, color=color)
                db.session.add(tag)
                tags.append(tag)
            db.session.commit()
            
            # Create sample posts
            post1 = Post(
                title='Chào mừng đến với CLB Karatedo Bách Khoa Hà Nội',
                content='Câu lạc bộ Karatedo Bách Khoa Hà Nội!',
                author_id=admin.id,
                status=PostStatus.PUBLISHED,
                published_at=datetime.now()
            )
            db.session.add(post1)
            post1.tags.append(tags[0])
            
            post2 = Post(
                title='Tại sao mình yêu karate',
                content='3 năm trong CLB, karate đã dạy mình rất nhiều điều.',
                author_id=member.id,
                status=PostStatus.PUBLISHED,
                published_at=datetime.now()
            )
            db.session.add(post2)
            post2.tags.append(tags[4])
            
            db.session.commit()
            print("✅ Sample data created")
            print("⚠️  Credentials: admin/admin123, member1/member123")
            
        else:
            # Normal startup - just ensure tables exist
            db.create_all()
            print("✅ Database tables ready")
            
except Exception as e:
    print(f"⚠️  Database init failed: {e}")
    print("Will try to start anyway...")

# Start Gunicorn
print("Starting Gunicorn...")
port = os.environ.get("PORT", "8000")
subprocess.run([
    "gunicorn",
    "--bind", f"0.0.0.0:{port}",
    "--workers", "4",
    "--timeout", "120",
    "wsgi:application"
])
