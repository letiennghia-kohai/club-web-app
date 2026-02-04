"""Media service for file upload and management."""
import os
import uuid
from datetime import datetime
from flask import current_app, url_for
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

# Cloudinary import (optional - will use local storage if not configured)
try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False


def _use_cloudinary():
    """Check if Cloudinary should be used."""
    if not CLOUDINARY_AVAILABLE:
        return False
    
    use_cloudinary = current_app.config.get('USE_CLOUDINARY', False)
    cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME', '')
    
    if use_cloudinary and cloud_name:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=current_app.config.get('CLOUDINARY_API_KEY', ''),
            api_secret=current_app.config.get('CLOUDINARY_API_SECRET', '')
        )
        return True
    
    return False


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
            
            # Get image dimensions
            width, height = image.size
            
            # Check if Cloudinary is enabled
            if _use_cloudinary():
                # Upload to Cloudinary
                import io
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
                img_byte_arr.seek(0)
                
                result = cloudinary.uploader.upload(
                    img_byte_arr,
                    folder='posts',
                    public_id=f'post_{post_id}_{uuid.uuid4().hex}',
                    resource_type='image'
                )
                
                # Create media record with Cloudinary URL
                media = Media(
                    post_id=post_id,
                    type=MediaType.IMAGE,
                    url=result['secure_url'],  # Cloudinary URL
                    filename=original_filename,
                    mime_type=file.content_type,
                    file_size=result.get('bytes', 0),
                    width=width,
                    height=height
                )
                
                current_app.logger.info(f'Post image uploaded to Cloudinary: {result["secure_url"]}')
            
            else:
                # Local storage fallback
                try:
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    image_folder = os.path.join(upload_folder, 'images')
                    os.makedirs(image_folder, exist_ok=True)
                    
                    filepath = os.path.join(image_folder, unique_filename)
                    image.save(filepath, optimize=True, quality=85)
                    
                    # Create media record with local path
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
                    
                    current_app.logger.info(f'Post image saved locally: {unique_filename}')
                
                except PermissionError:
                    current_app.logger.error('Cannot save post image - read-only filesystem')
                    return None, 'Lỗi: Không thể lưu ảnh (cần cấu hình Cloudinary)'
            
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
    
    @staticmethod
    def upload_avatar(file, user_id):
        """Upload and process user avatar."""
        if not file:
            return None, 'Không có file được chọn'
        
        # Validate file extension
        if not allowed_file(file.filename, 'image'):
            return None, 'Chỉ chấp nhận file ảnh (JPG, PNG, GIF, WebP)'
        
        # Validate MIME type
        if not validate_image_mime(file.content_type):
            return None, 'Loại file không hợp lệ'
        
        # Get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        # Avatar max 2MB
        max_avatar_size = 2 * 1024 * 1024
        if file_size > max_avatar_size:
            return None, 'Ảnh đại diện tối đa 2MB'
        
        try:
            # Generate unique filename
            original_filename = sanitize_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f'user_{user_id}_{uuid.uuid4().hex}.{ext}'
            
            # Create upload path
            upload_folder = current_app.config['UPLOAD_FOLDER']
            avatar_folder = os.path.join(upload_folder, 'avatars')
            os.makedirs(avatar_folder, exist_ok=True)
            
            filepath = os.path.join(avatar_folder, unique_filename)
            
            # Open and process image
            image = Image.open(file)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize to 400x400 (square crop from center)
            avatar_size = 400
            width, height = image.size
            
            # Crop to square from center
            if width > height:
                left = (width - height) // 2
                image = image.crop((left, 0, left + height, height))
            elif height > width:
                top = (height - width) // 2
                image = image.crop((0, top, width, top + width))
            
            # Resize to target size
            image = image.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            
            # Check if Cloudinary is enabled
            if _use_cloudinary():
                # Upload to Cloudinary
                import io
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG', quality=90, optimize=True)
                img_byte_arr.seek(0)
                
                result = cloudinary.uploader.upload(
                    img_byte_arr,
                    folder='avatars',
                    public_id=f'user_{user_id}_{uuid.uuid4().hex}',
                    overwrite=True,
                    resource_type='image'
                )
                
                avatar_url = result['secure_url']
                current_app.logger.info(f'Avatar uploaded to Cloudinary for user {user_id}')
                return avatar_url, None
            
            else:
                # Local storage fallback
                try:
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    avatar_folder = os.path.join(upload_folder, 'avatars')
                    os.makedirs(avatar_folder, exist_ok=True)
                    
                    filepath = os.path.join(avatar_folder, unique_filename)
                    image.save(filepath, optimize=True, quality=90)
                    
                    current_app.logger.info(f'Avatar uploaded locally for user {user_id}: {unique_filename}')
                    return unique_filename, None
                    
                except PermissionError:
                    current_app.logger.error('Cannot save avatar - read-only filesystem. Enable Cloudinary!')
                    return None, 'Lỗi: Không thể lưu ảnh (cần cấu hình Cloudinary cho production)'
            
        except Exception as e:
            current_app.logger.error(f'Error uploading avatar: {str(e)}')
            return None, f'Lỗi khi upload ảnh: {str(e)}'
    
    @staticmethod
    def delete_avatar(filename):
        """Delete avatar file."""
        if not filename:
            return True, None
        
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            filepath = os.path.join(upload_folder, 'avatars', filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            return True, None
        except Exception as e:
            current_app.logger.error(f'Error deleting avatar: {str(e)}')
            return False, 'Lỗi khi xóa ảnh đại diện'
