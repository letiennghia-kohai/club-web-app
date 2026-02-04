"""
Script to create sample confession posts and tag
Run with: venv\Scripts\python.exe create_confession_samples.py
"""
from app import create_app, db
from app.models.tag import Tag
from app.models.post import Post, PostStatus
from app.models.user import User
from datetime import datetime

app = create_app()

with app.app_context():
    # 1. Create Confession tag if not exists
    confession_tag = Tag.query.filter_by(slug='confession').first()
    if not confession_tag:
        confession_tag = Tag(
            name='Confession',
            slug='confession',
            color='#667eea'  # Purple gradient
        )
        db.session.add(confession_tag)
        db.session.commit()
        print("✓ Created Confession tag")
    else:
        print("✓ Confession tag already exists")
    
    # 2. Get admin user to create posts
    admin = User.query.filter_by(role='ADMIN').first()
    if not admin:
        # Try to get any user
        admin = User.query.first()
        if not admin:
            print("✗ No users found in database!")
            exit(1)
    
    print(f"Using user: {admin.username} ({admin.role})")

    
    # 3. Sample confession posts
    sample_confessions = [
        {
            'title': 'Kỷ niệm đáng nhớ trong lần thi đấu đầu tiên',
            'content': '''Mình còn nhớ như in lần đầu tiên tham gia giải thi đấu karate cấp trường. 
            
Tim đập thình thịch, tay run run khi đứng trên sàn thi đấu. Nhưng khi nghe tiếng trống, mọi lo lắng tan biến.

Dù không giành được huy chương, nhưng niềm tự hào khi hoàn thành bài kata trước đám đông vẫn còn mãi trong lòng.

Cảm ơn anh chị trong CLB đã luôn động viên và ủng hộ! 💪'''
        },
        {
            'title': 'Lời cảm ơn đến người thầy của tôi',
            'content': '''Thầy ơi, em muốn nói lời cảm ơn sâu sắc đến thầy.

Từ một người giảm cân, không tự tin, em đã tìm thấy bản thân mình qua karate. Thầy không chỉ dạy em võ thuật, mà còn dạy em về kỷ luật, kiên nhẫn và sự kiên trì.

Mỗi buổi tập với thầy là một bài học quý giá. Em sẽ cố gắng hơn nữa để không phụ lòng thầy! 🙏'''
        },
        {
            'title': 'Tại sao mình yêu karate',
            'content': '''3 năm trong CLB, mình nhận ra karate không chỉ là môn võ thuật.

Đó là nơi mình học cách tôn trọng người khác, kiểm soát bản thân, và không ngừng hoàn thiện.

Mỗi lần vượt qua một thử thách, mỗi lần lên đai mới, mình lại trở nên mạnh mẽ hơn - không chỉ về thể chất mà còn cả tinh thần.

Karate đã thay đổi cuộc sống mình! OSU! 🥋'''
        }
    ]
    
    # 4. Create confession posts
    created_count = 0
    for conf_data in sample_confessions:
        # Check if post with same title exists
        existing = Post.query.filter_by(title=conf_data['title']).first()
        if existing:
            print(f"⊘ Skipped: {conf_data['title']} (already exists)")
            continue
        
        post = Post(
            title=conf_data['title'],
            content=conf_data['content'],
            status=PostStatus.PUBLISHED,
            author_id=admin.id,
            published_at=datetime.utcnow()
        )
        db.session.add(post)
        db.session.flush()  # Get post ID
        
        # Add confession tag
        post.tags.append(confession_tag)
        created_count += 1
        print(f"✓ Created: {conf_data['title']}")
    
    db.session.commit()
    print(f"\n✅ Done! Created {created_count} confession posts")
    print(f"Total confession posts: {len(confession_tag.posts.filter_by(status=PostStatus.PUBLISHED).all())}")
