"""Notification blueprint for user notifications."""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.services.notification_service import NotificationService

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/notifications')
@login_required
def notifications():
    """Notification list page."""
    notifications = NotificationService.get_user_notifications(current_user.id, limit=50)
    unread_count = NotificationService.get_unread_count(current_user.id)
    
    return render_template(
        'member/notifications.html',
        notifications=notifications,
        unread_count=unread_count
    )


@notification_bp.route('/api/notifications')
@login_required
def api_notifications():
    """Get notifications as JSON for AJAX."""
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 10, type=int)
    
    notifications = NotificationService.get_user_notifications(
        current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': NotificationService.get_unread_count(current_user.id)
    })


@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """Mark single notification as read."""
    success, error = NotificationService.mark_as_read(notification_id, current_user.id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': error}), 400


@notification_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_as_read():
    """Mark all notifications as read."""
    success, error = NotificationService.mark_all_as_read(current_user.id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': error}), 400
