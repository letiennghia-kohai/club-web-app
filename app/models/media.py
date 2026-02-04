"""Media model with fixed relationships."""
from datetime import datetime
from app import db


class MediaType:
    """Media type constants."""
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'


class Media(db.Model):
    """Media model for images and videos."""
    
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)
    
    # File information (for uploaded files)
    file_path = db.Column(db.String(255), nullable=True)
    filename = db.Column(db.String(255), nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)  # in bytes
    
    # URL information (for embedded videos)
    url = db.Column(db.String(500), nullable=True)
    embed_html = db.Column(db.Text, nullable=True)  # Pre-generated embed code
    
    # Metadata
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # video duration in seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('Post', back_populates='media')
    
    def __repr__(self):
        return f'<Media {self.id}: {self.type}>'
    
    def is_image(self):
        """Check if media is an image."""
        return self.type == MediaType.IMAGE
    
    def is_video(self):
        """Check if media is a video."""
        return self.type == MediaType.VIDEO
    
    def is_uploaded(self):
        """Check if media is uploaded (vs embedded)."""
        return self.file_path is not None
    
    def is_embedded(self):
        """Check if media is embedded."""
        return self.url is not None
    
    def get_url(self):
        """Get media URL."""
        # If URL field is set (Cloudinary or embedded video), return it
        if self.url:
            return self.url
        # Otherwise construct local file URL
        if self.is_uploaded():
            return f'/static/uploads/{self.file_path}'
        return None

    
    def get_file_size_mb(self):
        """Get file size in MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    def to_dict(self):
        """Convert media to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'url': self.get_url(),
            'filename': self.filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'file_size_mb': self.get_file_size_mb(),
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'embed_html': self.embed_html,
            'is_uploaded': self.is_uploaded(),
            'is_embedded': self.is_embedded(),
            'created_at': self.created_at.isoformat()
        }
