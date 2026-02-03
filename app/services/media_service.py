"""Media service for file upload and management."""
import os
import uuid
from datetime import datetime
from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename
from app import db
from app.models.media import Media, MediaType
from app.utils.validators import (
    allowed_file,
    validate_file_size,
    validate_image_mime,
    validate_video_mime,
    validate_video_embed_url,
    get_video_embed_html,
    sanitize_filename
)


class MediaService:
    """Service for handling media uploads and processing."""
    
    @staticmethod
    def upload_image(file, post_id):
        """Upload and process image file."""
        if not file:
            return None, 'Không có file được chọn'
        
        # Validate file extension
        if not allowed_file(file.filename, 'image'):
            return None, 'Định dạng file không được hỗ trợ'
        
        # Validate MIME type
        if not validate_image_mime(file.content_type):
            return None, 'Loại file không hợp lệ'
        
        # Get file size (seek to end, get position, seek back to start)
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        # Validate file size
        if not validate_file_size(file_size):
            max_mb = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024) / (1024 * 1024)
            return None, f'Kích thước file vượt quá {max_mb}MB'
        
        try:
            # Generate unique filename
            original_filename = sanitize_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f'{uuid.uuid4().hex}.{ext}'
            
            # Create upload path
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image_folder = os.path.join(upload_folder, 'images')
            os.makedirs(image_folder, exist_ok=True)
            
            filepath = os.path.join(image_folder, unique_filename)
            
            # Save and optimize image
            image = Image.open(file)
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize if too large (max 1920px width)
            max_width = 1920
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            image.save(filepath, optimize=True, quality=85)
            
            # Get image dimensions
            width, height = image.size
            
            # Create media record
            media = Media(
                post_id=post_id,
                type=MediaType.IMAGE,
                file_path=f'images/{unique_filename}',
                filename=original_filename,
                mime_type=file.content_type,
                file_size=os.path.getsize(filepath),
                width=width,
                height=height
            )
            
            db.session.add(media)
            db.session.commit()
            
            return media, None
            
        except Exception as e:
            current_app.logger.error(f'Error uploading image: {str(e)}')
            return None, 'Lỗi khi upload ảnh'
    
    @staticmethod
    def upload_video(file, post_id):
        """Upload video file (optional, for demo only)."""
        if not file:
            return None, 'Không có file được chọn'
        
        # Validate file extension
        if not allowed_file(file.filename, 'video'):
            return None, 'Định dạng video không được hỗ trợ'
        
        # Validate MIME type
        if not validate_video_mime(file.content_type):
            return None, 'Loại file không hợp lệ'
        
        # Get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        # Validate file size (50MB limit for videos)
        max_video_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_video_size:
            return None, 'Video quá lớn (tối đa 50MB)'
        
        try:
            # Generate unique filename
            original_filename = sanitize_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f'{uuid.uuid4().hex}.{ext}'
            
            # Create upload path
            upload_folder = current_app.config['UPLOAD_FOLDER']
            video_folder = os.path.join(upload_folder, 'videos')
            os.makedirs(video_folder, exist_ok=True)
            
            filepath = os.path.join(video_folder, unique_filename)
            
            # Save video
            file.save(filepath)
            
            # Create media record
            media = Media(
                post_id=post_id,
                type=MediaType.VIDEO,
                file_path=f'videos/{unique_filename}',
                filename=original_filename,
                mime_type=file.content_type,
                file_size=os.path.getsize(filepath)
            )
            
            db.session.add(media)
            db.session.commit()
            
            current_app.logger.warning(
                f'Video uploaded to local storage. '
                f'Consider using embed URLs for production. File: {unique_filename}'
            )
            
            return media, None
            
        except Exception as e:
            current_app.logger.error(f'Error uploading video: {str(e)}')
            return None, 'Lỗi khi upload video'
    
    @staticmethod
    def add_video_embed(url, post_id):
        """Add embedded video from URL."""
        if not url:
            return None, 'URL không được để trống'
        
        # Validate URL
        if not validate_video_embed_url(url):
            return None, 'URL video không hợp lệ (chỉ hỗ trợ YouTube, Facebook, Google Drive)'
        
        try:
            # Generate embed HTML
            embed_html = get_video_embed_html(url)
            
            if not embed_html:
                return None, 'Không thể tạo embed code cho URL này'
            
            # Create media record
            media = Media(
                post_id=post_id,
                type=MediaType.VIDEO,
                url=url,
                embed_html=embed_html
            )
            
            db.session.add(media)
            db.session.commit()
            
            return media, None
            
        except Exception as e:
            current_app.logger.error(f'Error adding video embed: {str(e)}')
            return None, 'Lỗi khi thêm video'
    
    @staticmethod
    def delete_media(media_id):
        """Delete media and associated file."""
        media = Media.query.get(media_id)
        if not media:
            return False, 'Media không tồn tại'
        
        try:
            # Delete file if it's uploaded
            if media.is_uploaded() and media.file_path:
                upload_folder = current_app.config['UPLOAD_FOLDER']
                filepath = os.path.join(upload_folder, media.file_path)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            # Delete database record
            db.session.delete(media)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f'Error deleting media: {str(e)}')
            db.session.rollback()
            return False, 'Lỗi khi xóa media'
    
    @staticmethod
    def get_post_media(post_id):
        """Get all media for a post."""
        return Media.query.filter_by(post_id=post_id).order_by(Media.created_at).all()
