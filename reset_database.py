"""
Reset and Initialize Database
WARNING: This will DELETE ALL existing data!
"""
from app import create_app, db
from app.models.user import User, UserRole, UserStatus
from app.models.post import Post, PostStatus
from app.models.tag import Tag
from app.models.comment import Comment
from datetime import datetime, date
from werkzeug.security import generate_password_hash

def reset_database():
    """Drop all tables and recreate them."""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        
        print("🔨 Creating all tables with latest schema...")
        db.create_all()
        
        print("✅ Database schema created successfully!")
        
        # Create admin user
        print("\n👤 Creating admin user...")
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
        
        # Create sample member
        print("👤 Creating sample member...")
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
        print(f"✅ Admin ID: {admin.id}")
        print(f"✅ Member ID: {member.id}")
        
        # Create tags
        print("\n🏷️  Creating tags...")
        tags_data = [
            {'name': 'Thông báo', 'slug': 'thong-bao', 'color': '#3b82f6'},
            {'name': 'Sự kiện', 'slug': 'su-kien', 'color': '#10b981'},
            {'name': 'Thi đấu', 'slug': 'thi-dau', 'color': '#f59e0b'},
            {'name': 'Tuyển sinh', 'slug': 'tuyen-sinh', 'color': '#8b5cf6'},
            {'name': 'Confession', 'slug': 'confession', 'color': '#ec4899'},
        ]
        
        tags = []
        for tag_data in tags_data:
            tag = Tag(**tag_data)
            db.session.add(tag)
            tags.append(tag)
        
        db.session.commit()
        print(f"✅ Created {len(tags)} tags")
        
        # Create sample posts
        print("\n📝 Creating sample posts...")
        
        # Admin post
        post1 = Post(
            title='Chào mừng đến với CLB Karatedo Bách Khoa Hà Nội',
            content='''# Giới thiệu

Câu lạc bộ Karatedo Bách Khoa Hà Nội là một trong những câu lạc bộ võ thuật lâu đời nhất tại trường Đại học Bách Khoa Hà Nội.

## Lịch tập

- Thứ 2, 4, 6: 18h00 - 20h00
- Địa điểm: Nhà tập C9

## Liên hệ

Email: karatebk@hust.edu.vn
''',
            author_id=admin.id,
            status=PostStatus.PUBLISHED,
            published_at=datetime.now()
        )
        db.session.add(post1)
        post1.tags.append(tags[0])  # Thông báo
        
        # Member confession post
        post2 = Post(
            title='Tại sao mình yêu karate',
            content='''3 năm trong CLB, mình nhận ra karate không chỉ là môn võ thuật. Đó là nơi mình học cách tôn trọng, kỷ luật và không ngừng cố gắng.

Từ một người nhút nhát, karate đã giúp mình tự tin hơn rất nhiều. Cảm ơn CLB đã cho mình một gia đình thứ hai!

#karate #clbkaratebk #motivation
''',
            author_id=member.id,
            status=PostStatus.PUBLISHED,
            published_at=datetime.now()
        )
        db.session.add(post2)
        post2.tags.append(tags[4])  # Confession
        
        db.session.commit()
        print(f"✅ Created 2 sample posts")
        
        print("\n" + "="*50)
        print("✅ DATABASE RESET COMPLETE!")
        print("="*50)
        print("\n📊 Summary:")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Posts: {Post.query.count()}")
        print(f"  - Tags: {Tag.query.count()}")
        print("\n🔑 Login credentials:")
        print("  Admin: admin / admin123")
        print("  Member: member1 / member123")
        print("\n" + "="*50)

if __name__ == '__main__':
    confirm = input("⚠️  WARNING: This will DELETE ALL DATA! Type 'YES' to confirm: ")
    if confirm == 'YES':
        reset_database()
    else:
        print("❌ Cancelled")
