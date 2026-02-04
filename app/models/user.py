"""User model with fixed relationships."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from enum import Enum


# Belt progression order - Kyu system (from lowest to highest)
BELT_ORDER = [
    'Kuy 10',  # Beginner
    'Kuy 9',
    'Kuy 8',
    'Kuy 7',
    'Kuy 6',
    'Kuy 5',
    'Kuy 4',
    'Kuy 3',
    'Kuy 2',
    'Kuy 1',
    # Black belt dan ranks
    'Đai đen nhất đẳng',  # 1st Dan
    'Đai đen nhị đẳng',   # 2nd Dan
    'Đai đen tam đẳng',   # 3rd Dan
    'Đai đen tứ đẳng',    # 4th Dan
    'Đai đen ngũ đẳng',   # 5th Dan
]


class UserRole:
    """User role constants."""
    ADMIN = 'ADMIN'
    MEMBER = 'MEMBER'


class UserStatus:
    """User status constants."""
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class User(UserMixin, db.Model):
    """User model for authentication and member management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.MEMBER)
    
    # Profile information
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    belt = db.Column(db.String(50), nullable=True)  # Cấp đai/Kyu
    date_of_birth = db.Column(db.Date, nullable=True)  # Ngày sinh
    phone_number = db.Column(db.String(15), nullable=True)  # Số điện thoại
    facebook_link = db.Column(db.String(255), nullable=True)  # Facebook/Social media
    avatar = db.Column(db.String(255), nullable=True)  # Avatar filename
    join_date = db.Column(db.Date, nullable=True)  # Ngày gia nhập
    status = db.Column(db.String(20), nullable=False, default=UserStatus.ACTIVE)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #  Relationships
    posts = db.relationship('Post', back_populates='author', lazy='dynamic', foreign_keys='Post.author_id', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def is_member(self):
        """Check if user is member."""
        return self.role == UserRole.MEMBER
    
    def is_active_user(self):
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'belt': self.belt,
            'student_id': self.student_id,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
    
    def get_avatar_url(self):
        """Get avatar URL or None if no avatar."""
        if self.avatar:
            # If avatar is already a full URL (Cloudinary), return it directly
            if self.avatar.startswith(('http://', 'https://')):
                return self.avatar
            # Otherwise it's a local filename
            return f'/static/uploads/avatars/{self.avatar}'
        return None
    
    def get_initials(self):
        """Get user initials for avatar fallback."""
        if not self.full_name:
            return '?'
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f'{parts[0][0]}{parts[-1][0]}'.upper()
        return self.full_name[0].upper()
