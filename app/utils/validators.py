"""File and input validators."""
import os
import re
from urllib.parse import urlparse
from flask import current_app


def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed."""
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())
    elif file_type == 'video':
        allowed_extensions = current_app.config.get('ALLOWED_VIDEO_EXTENSIONS', set())
    else:
        return False
    
    return ext in allowed_extensions


def validate_file_size(file_size, max_size=None):
    """Validate file size."""
    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)
    
    return file_size <= max_size


def validate_mime_type(mime_type, allowed_types):
    """Validate MIME type."""
    if not mime_type:
        return False
    
    # Check exact match
    if mime_type in allowed_types:
        return True
    
    # Check wildcard match (e.g., 'image/*')
    mime_category = mime_type.split('/')[0]
    wildcard = f'{mime_category}/*'
    return wildcard in allowed_types


def validate_image_mime(mime_type):
    """Validate image MIME type."""
    allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    return validate_mime_type(mime_type, allowed)


def validate_video_mime(mime_type):
    """Validate video MIME type."""
    allowed = ['video/mp4', 'video/webm', 'video/quicktime']
    return validate_mime_type(mime_type, allowed)


def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal."""
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Remove any non-alphanumeric characters except dots and underscores
    filename = re.sub(r'[^\w\.-]', '_', filename)
    
    return filename


def validate_youtube_url(url):
    """Validate and extract YouTube video ID."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    match = re.match(youtube_regex, url)
    if match:
        return match.group(6)  # Return video ID
    return None


def validate_facebook_video_url(url):
    """Validate Facebook video URL."""
    facebook_regex = (
        r'(https?://)?(www\.)?facebook\.com/'
        r'.*/(videos?|watch)/.*'
    )
    return bool(re.match(facebook_regex, url))


def validate_drive_url(url):
    """Validate Google Drive URL."""
    drive_regex = r'(https?://)?(www\.)?drive\.google\.com/file/d/([^/]+)'
    match = re.match( drive_regex, url)
    if match:
        return match.group(3)  # Return file ID
    return None


def validate_video_embed_url(url):
    """Validate any supported video embed URL."""
    if not url:
        return False
    
    # Check if URL is valid
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False
    except:
        return False
    
    # Check if it's from a supported platform
    return (
        validate_youtube_url(url) or
        validate_facebook_video_url(url) or
        validate_drive_url(url)
    )


def get_video_embed_html(url):
    """Generate embed HTML for video URL."""
    # YouTube
    youtube_id = validate_youtube_url(url)
    if youtube_id:
        return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{youtube_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    
    # Facebook (use Facebook's embed)
    if validate_facebook_video_url(url):
        return f'<iframe src="https://www.facebook.com/plugins/video.php?href={url}" width="560" height="315" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>'
    
    # Google Drive
    drive_id = validate_drive_url(url)
    if drive_id:
        return f'<iframe src="https://drive.google.com/file/d/{drive_id}/preview" width="560" height="315" allow="autoplay"></iframe>'
    
    return None


def sanitize_html(html_content):
    """Sanitize HTML content to prevent XSS."""
    import bleach
    
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'code', 'pre'
    ]
    
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
    }
    
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
