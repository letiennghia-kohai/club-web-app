"""Notification service for creating and managing notifications."""
from flask import current_app, url_for
from app import db
from app.models.notification import Notification, NotificationType
from app.models.user import User, UserStatus
from app.models.post import Post
from app.models.comment import Comment
from typing import Optional, List, Tuple


class NotificationService:
    """Service for handling notifications."""
    
    MAX_NOTIFICATIONS_PER_USER = 100
    
    @staticmethod
    def notify_all_users(post: Post) -> Tuple[int, Optional[str]]:
        """
        Create notifications for all active users when admin posts.
        
        Args:
            post: The newly created post
            
        Returns:
            Tuple of (number of notifications created, error message)
        """
        try:
            # Get all active users except the post author
            users = User.query.filter(
                User.status == UserStatus.ACTIVE,
                User.id != post.author_id
            ).all()
            
            count = 0
            for user in users:
                notification = Notification(
                    user_id=user.id,
                    type=NotificationType.ADMIN_POST,
                    title='Bài viết mới từ Admin',
                    message=f'Admin vừa đăng: {post.title[:100]}',
                    link=url_for('public.post_detail', post_id=post.id, _external=False)
                )
                db.session.add(notification)
                count += 1
            
            # Cleanup old notifications per user
            NotificationService._cleanup_old_notifications()
            
            db.session.commit()
            current_app.logger.info(f'Created {count} notifications for admin post {post.id}')
            return count, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating notifications: {str(e)}')
            return 0, str(e)
    
    @staticmethod
    def notify_post_author(comment: Comment) -> Tuple[bool, Optional[str]]:
        """
        Create notification for post author when someone comments.
        
        Args:
            comment: The newly created comment
            
        Returns:
            Tuple of (success, error message)
        """
        try:
            # Don't notify if commenting on own post
            if comment.user_id == comment.post.author_id:
                return True, None
            
            # Don't notify if author is not active
            author = comment.post.author
            if author.status != UserStatus.ACTIVE:
                return True, None
            
            notification = Notification(
                user_id=comment.post.author_id,
                type=NotificationType.POST_COMMENT,
                title='Bình luận mới',
                message=f'{comment.user.full_name} đã bình luận vào bài viết của bạn',
                link=url_for('public.post_detail', post_id=comment.post_id, _external=False) + f'#comment-{comment.id}'
            )
            db.session.add(notification)
            db.session.commit()
            
            current_app.logger.info(f'Created notification for post author {comment.post.author_id}')
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating comment notification: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: If True, only return unread notifications
            limit: Maximum number of notifications to return
            
        Returns:
            List of Notification objects
        """
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        return notifications
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        return count
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for security check)
            
        Returns:
            Tuple of (success, error message)
        """
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return False, 'Notification not found'
            
            notification.is_read = True
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error marking notification as read: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def mark_all_as_read(user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (success, error message)
        """
        try:
            Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({'is_read': True})
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error marking all as read: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def _cleanup_old_notifications():
        """Delete old notifications if user has too many."""
        try:
            # For each user, keep only the latest MAX_NOTIFICATIONS_PER_USER
            users_with_many = db.session.query(Notification.user_id).group_by(
                Notification.user_id
            ).having(
                db.func.count(Notification.id) > NotificationService.MAX_NOTIFICATIONS_PER_USER
            ).all()
            
            for (user_id,) in users_with_many:
                # Get IDs of notifications to keep
                keep_ids = db.session.query(Notification.id).filter_by(
                    user_id=user_id
                ).order_by(
                    Notification.created_at.desc()
                ).limit(NotificationService.MAX_NOTIFICATIONS_PER_USER).all()
                
                keep_ids = [nid[0] for nid in keep_ids]
                
                # Delete old ones
                Notification.query.filter(
                    Notification.user_id == user_id,
                    ~Notification.id.in_(keep_ids)
                ).delete(synchronize_session=False)
            
        except Exception as e:
            current_app.logger.error(f'Error cleaning up notifications: {str(e)}')
