"""Helper utilities."""
from datetime import datetime
import markdown as md
from app.utils.validators import sanitize_html


def format_datetime(dt, format='%d/%m/%Y %H:%M'):
    """Format datetime to string."""
    if isinstance(dt, datetime):
        return dt.strftime(format)
    return ''


def format_date(dt, format='%d/%m/%Y'):
    """Format date to string."""
    if isinstance(dt, datetime):
        return dt.strftime(format)
    return ''


def time_ago(dt):
    """Get human-readable time ago."""
    if not isinstance(dt, datetime):
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'vừa xong'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} phút trước'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} giờ trước'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} ngày trước'
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f'{weeks} tuần trước'
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f'{months} tháng trước'
    else:
        years = int(seconds / 31536000)
        return f'{years} năm trước'


def markdown_to_html(text):
    """Convert Markdown to HTML."""
    if not text:
        return ''
    
    # Convert markdown to HTML
    html = md.markdown(
        text,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists'
        ]
    )
    
    # Sanitize HTML to prevent XSS
    return sanitize_html(html)


def truncate_text(text, length=100, suffix='...'):
    """Truncate text to specified length."""
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix


def get_file_extension(filename):
    """Get file extension from filename."""
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def format_file_size(bytes_size):
    """Format file size in human-readable format."""
    if not bytes_size:
        return '0 B'
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f'{size:.2f} {units[unit_index]}'


def get_belt_color_class(belt):
    """Get CSS class for belt color."""
    belt_colors = {
        'Trắng': 'belt-white',
        'Vàng': 'belt-yellow',
        'Cam': 'belt-orange',
        'Xanh lá': 'belt-green',
        'Xanh dương': 'belt-blue',
        'Nâu': 'belt-brown',
        'Đen': 'belt-black',
    }
    return belt_colors.get(belt, 'belt-default')


def get_post_status_badge(status):
    """Get Bootstrap badge class for post status."""
    status_badges = {
        'DRAFT': 'secondary',
        'PENDING_APPROVAL': 'warning',
        'APPROVED': 'info',
        'PUBLISHED': 'success',
        'REJECTED': 'danger',
    }
    return status_badges.get(status, 'secondary')


def get_post_status_text(status):
    """Get Vietnamese text for post status."""
    status_text = {
        'DRAFT': 'Bản nháp',
        'PENDING_APPROVAL': 'Chờ duyệt',
        'APPROVED': 'Đã duyệt',
        'PUBLISHED': 'Đã đăng',
        'REJECTED': 'Từ chối',
    }
    return status_text.get(status, status)
