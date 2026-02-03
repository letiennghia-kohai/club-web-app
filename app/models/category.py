"""Category model for organizing posts."""
from datetime import datetime
from app import db


class Category(db.Model):
    """Post category model."""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)  # Display order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    @property
    def post_count(self):
        """Get number of published posts in this category."""
        from app.models.post import PostStatus
        return self.posts.filter_by(status=PostStatus.PUBLISHED).count()
