"""Comment service for managing comments."""
from flask import current_app
from sqlalchemy import or_
from app import db
from app.models.comment import Comment
from app.models.user import User


class CommentService:
    """Service for comment management."""
    
    @staticmethod
    def search_comments(query, page=1, per_page=20):
        """Search comments by content or author name."""
        if not query:
            # Return all comments if no query
            return Comment.query.join(
                Comment.post
            ).order_by(Comment.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        
        search_pattern = f'%{query}%'
        
        # Search in comment content, user full name, or guest name
        return Comment.query.outerjoin(
            User, User.id == Comment.user_id
        ).filter(
            or_(
                Comment.content.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
                Comment.guest_name.ilike(search_pattern)
            )
        ).order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_all_comments(page=1, per_page=20):
        """Get all comments with pagination."""
        return Comment.query.order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def delete_comment(comment_id):
        """Delete a comment."""
        comment = Comment.query.get(comment_id)
        if not comment:
            return False, 'Bình luận không tồn tại'
        
        try:
            db.session.delete(comment)
            db.session.commit()
            current_app.logger.info(f'Comment deleted: {comment_id}')
            return True, None
        except Exception as e:
            current_app.logger.error(f'Error deleting comment: {str(e)}')
            db.session.rollback()
            return False, 'Lỗi khi xóa bình luận'
