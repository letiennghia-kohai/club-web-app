"""Post model with fixed relationships."""
from datetime import datetime
from app import db


class PostStatus:
    """Post status constants."""
    DRAFT = 'DRAFT'
    PENDING_APPROVAL = 'PENDING_APPROVAL'
    APPROVED = 'APPROVED'
    PUBLISHED = 'PUBLISHED'
    REJECTED = 'REJECTED'


class Post(db.Model):
    """Post model for content management."""
    
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=PostStatus.DRAFT, index=True)
    
    # Category
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Approval information
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships - using back_populates
    author = db.relationship('User', foreign_keys=[author_id], back_populates='posts')
    media = db.relationship('Media', back_populates='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='post', lazy='dynamic', cascade='all, delete-orphan')
    
    # Tags relationship (many-to-many)
    tags = db.relationship('Tag', secondary='post_tags', back_populates='posts', lazy='dynamic')
    
    def __repr__(self):
        return f'<Post {self.id}: {self.title}>'
    
    def can_edit(self, user):
        """Check if user can edit this post."""
        if user.is_admin():
            return True
        # Members can only edit their own drafts and pending posts
        if self.author_id == user.id:
            return self.status in [PostStatus.DRAFT, PostStatus.PENDING_APPROVAL]
        return False
    
    def can_delete(self, user):
        """Check if user can delete this post."""
        if user.is_admin():
            return True
        # Members can only delete their own drafts
        if self.author_id == user.id:
            return self.status == PostStatus.DRAFT
        return False
    
    def is_admin_post(self):
        """Check if this post was created by an admin."""
        return self.author and self.author.is_admin()
    
    def submit_for_approval(self):
        """Submit post for approval."""
        if self.status == PostStatus.DRAFT:
            self.status = PostStatus.PENDING_APPROVAL
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def approve(self, reviewer_user):
        """Approve and publish post."""
        if self.status == PostStatus.PENDING_APPROVAL:
            self.status = PostStatus.PUBLISHED
            self.reviewed_by_id = reviewer_user.id
            self.reviewed_at = datetime.utcnow()
            self.published_at = datetime.utcnow()
            return True
        return False
    
    def reject(self, reviewer_user, reason=None):
        """Reject post."""
        if self.status == PostStatus.PENDING_APPROVAL:
            self.status = PostStatus.REJECTED
            self.reviewed_by_id = reviewer_user.id
            self.reviewed_at = datetime.utcnow()
            self.rejection_reason = reason
            return True
        return False
    
    def publish_directly(self):
        """Publish post directly (admin only)."""
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        return True
    
    def is_published(self):
        """Check if post is published."""
        return self.status == PostStatus.PUBLISHED
    
    def get_media_images(self):
        """Get all image media for this post."""
        from app.models.media import MediaType
        return self.media.filter_by(type=MediaType.IMAGE).all()
    
    def get_media_videos(self):
        """Get all video media for this post."""
        from app.models.media import MediaType
        return self.media.filter_by(type=MediaType.VIDEO).all()
    
    def to_dict(self, include_content=True):
        """Convert post to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'status': self.status,
            'author': self.author.to_dict() if self.author else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }
        
        if include_content:
            data['content'] = self.content
            data['media'] = [m.to_dict() for m in self.media.all()]
            data['comments_count'] = self.comments.count()
        
        return data
