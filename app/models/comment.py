"""Comment model with fixed relationships."""
from datetime import datetime
from app import db


class Comment(db.Model):
    """Comment model for post discussions."""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # User can be null for guest comments
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Guest information (for anonymous comments)
    guest_name = db.Column(db.String(100), nullable=True)
    
    # Content
    content = db.Column(db.Text, nullable=False)
    
    # Moderation
    is_approved = db.Column(db.Boolean, nullable=False, default=True)
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'
    
    def is_guest_comment(self):
        """Check if comment is from a guest."""
        return self.user_id is None
    
    def get_author_name(self):
        """Get comment author name."""
        if self.user:
            return self.user.full_name
        return self.guest_name or 'Khách'
    
    def can_delete(self, user):
        """Check if user can delete this comment."""
        if user.is_admin():
            return True
        # Users can delete their own comments
        if self.user_id == user.id:
            return True
        return False
    
    def to_dict(self):
        """Convert comment to dictionary."""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'author_name': self.get_author_name(),
            'is_guest': self.is_guest_comment(),
            'content': self.content,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat()
        }
