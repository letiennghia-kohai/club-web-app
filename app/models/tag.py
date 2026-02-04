"""Tag model for post labeling."""
from datetime import datetime
from app import db


# Association table for many-to-many relationship
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Tag(db.Model):
    """Tag model for categorizing posts."""
    
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), default='#6c757d')  # Hex color for badge display
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    posts = db.relationship('Post', secondary=post_tags, back_populates='tags', lazy='dynamic')
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    @property
    def post_count(self):
        """Get number of published posts with this tag."""
        from app.models.post import PostStatus
        return self.posts.filter_by(status=PostStatus.PUBLISHED).count()
    
    @staticmethod
    def generate_slug(name):
        """Generate URL-friendly slug from Vietnamese name."""
        import re
        import unicodedata
        
        # Normalize Vietnamese characters
        name = name.lower().strip()
        
        # Vietnamese character mapping
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'đ': 'd',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
        }
        
        for viet_char, latin_char in vietnamese_map.items():
            name = name.replace(viet_char, latin_char)
        
        # Remove non-alphanumeric characters (except spaces and hyphens)
        name = re.sub(r'[^\w\s-]', '', name)
        
        # Replace spaces with hyphens
        name = re.sub(r'[\s]+', '-', name)
        
        # Remove consecutive hyphens
        name = re.sub(r'-+', '-', name)
        
        # Remove leading/trailing hyphens
        return name.strip('-')
