"""Notification model for user notifications."""
from datetime import datetime
from enum import Enum
from app import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship


class NotificationType(Enum):
    """Types of notifications."""
    ADMIN_POST = "admin_post"      # Admin đăng bài mới
    POST_COMMENT = "post_comment"  # Có comment vào bài của user


class Notification(db.Model):
    """Notification model."""
    __tablename__ = 'notification'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(500), nullable=False)
    link = Column(String(500))  # URL đến bài viết
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship('User', backref='notifications', lazy=True)
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type.value} for user {self.user_id}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_time_ago(self):
        """Get human-readable time ago string."""
        if not self.created_at:
            return ''
        
        now = datetime.utcnow()
        diff = now - self.created_at
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'Vừa xong'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} phút trước'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} giờ trước'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{days} ngày trước'
        else:
            weeks = int(seconds / 604800)
            return f'{weeks} tuần trước'
