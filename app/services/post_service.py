"""Post service for content management."""
from datetime import datetime
from flask import current_app
from app import db
from app.models.post import Post, PostStatus
from app.models.user import UserRole


class PostService:
    """Service for post management and workflow."""
    
    @staticmethod
    def create_post(title, content, author, status=PostStatus.DRAFT):
        """Create a new post."""
        try:
            post = Post(
                title=title,
                content=content,
                status=status,
                author_id=author.id
            )
            
            # Admin can publish directly
            if author.is_admin() and status == PostStatus.PUBLISHED:
                post.published_at = datetime.utcnow()
            
            db.session.add(post)
            db.session.commit()
            
            return post, None
            
        except Exception as e:
            current_app.logger.error(f'Error creating post: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi tạo bài viết'
    
    @staticmethod
    def update_post(post_id, title=None, content=None, user=None):
        """Update existing post."""
        post = Post.query.get(post_id)
        if not post:
            return None, 'Bài viết không tồn tại'
        
        # Check permissions
        if user and not post.can_edit(user):
            return None, 'Bạn không có quyền chỉnh sửa bài viết này'
        
        try:
            if title:
                post.title = title
            if content:
                post.content = content
            
            post.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return post, None
            
        except Exception as e:
            current_app.logger.error(f'Error updating post: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi cập nhật bài viết'
    
    @staticmethod
    def delete_post(post_id, user):
        """Delete post."""
        post = Post.query.get(post_id)
        if not post:
            return False, 'Bài viết không tồn tại'
        
        # Check permissions
        if not post.can_delete(user):
            return False, 'Bạn không có quyền xóa bài viết này'
        
        try:
            db.session.delete(post)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f'Error deleting post: {str(e)}')
            db.session.rollback()
            return False, 'Lỗi khi xóa bài viết'
    
    @staticmethod
    def submit_for_approval(post_id, user):
        """Submit post for approval."""
        post = Post.query.get(post_id)
        if not post:
            return None, 'Bài viết không tồn tại'
        
        # Check ownership
        if post.author_id != user.id and not user.is_admin():
            return None, 'Bạn không có quyền gửi bài viết này'
        
        if post.status != PostStatus.DRAFT:
            return None, 'Chỉ có thể gửi duyệt bài viết ở trạng thái Bản nháp'
        
        try:
            post.submit_for_approval()
            db.session.commit()
            
            current_app.logger.info(f'Post {post_id} submitted for approval by user {user.id}')
            
            return post, None
            
        except Exception as e:
            current_app.logger.error(f'Error submitting post: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi gửi bài viết'
    
    @staticmethod
    def approve_post(post_id, reviewer):
        """Approve and publish post."""
        if not reviewer.is_admin():
            return None, 'Chỉ Admin mới có quyền duyệt bài'
        
        post = Post.query.get(post_id)
        if not post:
            return None, 'Bài viết không tồn tại'
        
        if post.status != PostStatus.PENDING_APPROVAL:
            return None, 'Chỉ có thể duyệt bài viết đang chờ duyệt'
        
        try:
            post.approve(reviewer)
            db.session.commit()
            
            current_app.logger.info(f'Post {post_id} approved by admin {reviewer.id}')
            
            return post, None
            
        except Exception as e:
            current_app.logger.error(f'Error approving post: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi duyệt bài viết'
    
    @staticmethod
    def reject_post(post_id, reviewer, reason=None):
        """Reject post."""
        if not reviewer.is_admin():
            return None, 'Chỉ Admin mới có quyền từ chối bài'
        
        post = Post.query.get(post_id)
        if not post:
            return None, 'Bài viết không tồn tại'
        
        if post.status != PostStatus.PENDING_APPROVAL:
            return None, 'Chỉ có thể từ chối bài viết đang chờ duyệt'
        
        try:
            post.reject(reviewer, reason)
            db.session.commit()
            
            current_app.logger.info(f'Post {post_id} rejected by admin {reviewer.id}')
            
            return post, None
            
        except Exception as e:
            current_app.logger.error(f'Error rejecting post: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi từ chối bài viết'
    
    @staticmethod
    def get_published_posts(page=1, per_page=12):
        """Get published posts with pagination."""
        return Post.query.filter_by(
            status=PostStatus.PUBLISHED
        ).order_by(
            Post.published_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @staticmethod
    def get_pending_posts():
        """Get posts pending approval."""
        return Post.query.filter_by(
            status=PostStatus.PENDING_APPROVAL
        ).order_by(
            Post.created_at.desc()
        ).all()
    
    @staticmethod
    def get_user_posts(user_id, include_all=False):
        """Get posts by user."""
        query = Post.query.filter_by(author_id=user_id)
        
        if not include_all:
            # Exclude rejected posts for non-admin users
            query = query.filter(Post.status != PostStatus.REJECTED)
        
        return query.order_by(Post.created_at.desc()).all()
    
    @staticmethod
    def search_posts(keyword, page=1, per_page=12):
        """Search published posts by keyword."""
        return Post.query.filter(
            Post.status == PostStatus.PUBLISHED,
            db.or_(
                Post.title.ilike(f'%{keyword}%'),
                Post.content.ilike(f'%{keyword}%')
            )
        ).order_by(
            Post.published_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @staticmethod
    def admin_search_posts(query, page=1, per_page=20):
        """Search all posts including drafts (admin only)."""
        from sqlalchemy import or_
        
        if not query:
            return Post.query.order_by(Post.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        
        search_pattern = f'%{query}%'
        return Post.query.filter(
            or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern)
            )
        ).order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_all_posts():
        """Get all posts (admin function)."""
        return Post.query.order_by(Post.created_at.desc()).all()
    
    @staticmethod
    def get_posts_by_tag(tag_id, page=1, per_page=12):
        """Get published posts filtered by tag."""
        from app.models.tag import Tag
        
        tag = Tag.query.get(tag_id)
        if not tag:
            return Post.query.filter_by(id=0).paginate(page=page, per_page=per_page, error_out=False)
        
        return tag.posts.filter_by(
            status=PostStatus.PUBLISHED
        ).order_by(
            Post.published_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @staticmethod
    def get_published_posts_except_tag(tag_id, page=1, per_page=12):
        """Get published posts excluding specific tag."""
        from app.models.tag import post_tags
        
        # Get posts that don't have the specified tag
        subquery = db.session.query(post_tags.c.post_id).filter(
            post_tags.c.tag_id == tag_id
        )
        
        return Post.query.filter(
            Post.status == PostStatus.PUBLISHED,
            ~Post.id.in_(subquery)
        ).order_by(
            Post.published_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
