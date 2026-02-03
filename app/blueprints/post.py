"""Post blueprint (shared routes)."""
from flask import Blueprint, send_from_directory, current_app, abort
import os

post_bp = Blueprint('post', __name__)


@post_bp.route('/media/<path:filename>')
def serve_media(filename):
    """Serve uploaded media files."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Security: prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    filepath = os.path.join(upload_folder, filename)
    
    if not os.path.exists(filepath):
        abort(404)
    
    # Get directory and filename
    directory = os.path.dirname(filepath)
    file_basename = os.path.basename(filepath)
    
    return send_from_directory(directory, file_basename)
