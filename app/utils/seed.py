"""Database seeding utilities."""
from datetime import datetime, date
from app import db
from app.models import User, Post, PostStatus
from app.models.user import UserRole, UserStatus
import os


def seed_data():
    """Seed initial data into database."""
    
    # Create admin user
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin@123456')
    admin_full_name = os.getenv('ADMIN_FULL_NAME', 'Administrator')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@karateclub.edu.vn')
    
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(
            username=admin_username,
            full_name=admin_full_name,
            email=admin_email,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            belt='Đai đen nhất đẳng',  # Black belt 1st Dan
            join_date=date(2020, 1, 1)
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        print(f'✓ Created admin user: {admin_username}')
    
    # Create sample members
    sample_members = [
        {
            'username': 'member1',
            'password': 'Member@123',
            'full_name': 'Nguyễn Văn A',
            'email': 'nguyenvana@example.com',
            'student_id': '20210001',
            'belt': 'Kuy 3',  # Advanced level
            'join_date': date(2021, 9, 1)
        },
        {
            'username': 'member2',
            'password': 'Member@123',
            'full_name': 'Trần Thị B',
            'email': 'tranthib@example.com',
            'student_id': '20210002',
            'belt': 'Kuy 5',  # Intermediate level
            'join_date': date(2021, 9, 1)
        },
        {
            'username': 'member3',
            'password': 'Member@123',
            'full_name': 'Lê Văn C',
            'email': 'levanc@example.com',
            'student_id': '20220001',
            'belt': 'Kuy 8',  # Beginner level
            'join_date': date(2022, 9, 1)
        }
    ]
    
    for member_data in sample_members:
        existing = User.query.filter_by(username=member_data['username']).first()
        if not existing:
            member = User(
                username=member_data['username'],
                full_name=member_data['full_name'],
                email=member_data['email'],
                student_id=member_data['student_id'],
                role=UserRole.MEMBER,
                status=UserStatus.ACTIVE,
                belt=member_data['belt'],
                join_date=member_data['join_date']
            )
            member.set_password(member_data['password'])
            db.session.add(member)
            print(f'✓ Created member: {member_data["username"]}')
    
    # Create sample posts
    sample_posts = [
        {
            'title': 'Chào mừng đến với CLB Karate Bách Khoa',
            'content': '''# Chào mừng các bạn!

CLB Karate Bách Khoa là một trong những câu lạc bộ võ thuật lâu đời nhất tại trường Đại học Bách Khoa.

## Về CLB

- Thành lập năm 2010
- Hơn 200 thành viên
- Nhiều giải thưởng quốc gia và quốc tế

## Hoạt động

Chúng tôi tổ chức luyện tập thường xuyên:
- Thứ 2, 4, 6: 18:00 - 20:00
- Địa điểm: Nhà thi đấu A

Hãy tham gia cùng chúng tôi!''',
            'status': PostStatus.PUBLISHED,
            'author': admin
        },
        {
            'title': 'Khai giảng khóa học mới Karate cho người mới bắt đầu',
            'content': '''# Khóa học Karate cho người mới bắt đầu

CLB Karate Bách Khoa thông báo **khai giảng khóa học mới** dành cho các bạn mới tham gia.

## Thông tin khóa học

- **Thời gian**: Bắt đầu từ tuần sau
- **Học phí**: Miễn phí cho sinh viên
- **Yêu cầu**: Không cần kinh nghiệm

## Đăng ký

Liên hệ: admin@karateclub.edu.vn''',
            'status': PostStatus.PUBLISHED,
            'author': admin
        }
    ]
    
    for post_data in sample_posts:
        existing = Post.query.filter_by(title=post_data['title']).first()
        if not existing:
            post = Post(
                title=post_data['title'],
                content=post_data['content'],
                status=post_data['status'],
                author=post_data['author'],
                published_at=datetime.utcnow() if post_data['status'] == PostStatus.PUBLISHED else None
            )
            db.session.add(post)
            print(f'✓ Created post: {post_data["title"]}')
    
    # Commit all changes
    db.session.commit()
    print('\n✅ Database seeded successfully!')
    print(f'\nDefault login credentials:')
    print(f'  Admin - Username: {admin_username}, Password: {admin_password}')
    print(f'  Member - Username: member1, Password: Member@123')
    print(f'\n⚠️  IMPORTANT: Change the admin password after first login!')
