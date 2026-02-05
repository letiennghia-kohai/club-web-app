"""Public blueprint."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app import db
from app.models.post import Post, PostStatus
from app.models.comment import Comment
from app.models.tag import Tag
from app.services.notification_service import NotificationService
from app.services.post_service import PostService

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """Homepage with published posts."""
    
    page = request.args.get('page', 1, type=int)
    tag_slug = request.args.get('tag', None)
    
    # Get all tags for filter tabs
    all_tags = Tag.query.order_by(Tag.name).all()
    
    # Find confession tag
    confession_tag = Tag.query.filter_by(slug='confession').first()
    
    # Filter by tag if specified
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
        pagination = PostService.get_posts_by_tag(tag.id, page=page, per_page=12)
        selected_tag = tag
        confession_posts = []
    else:
        # Get regular posts (exclude confession)
        if confession_tag:
            pagination = PostService.get_published_posts_except_tag(confession_tag.id, page=page, per_page=12)
            # Get confession posts separately
            confession_posts = PostService.get_posts_by_tag(confession_tag.id, page=1, per_page=6).items
        else:
            pagination = PostService.get_published_posts(page=page, per_page=12)
            confession_posts = []
        selected_tag = None
    
    return render_template(
        'public/index.html',
        posts=pagination.items,
        pagination=pagination,
        all_tags=all_tags,
        selected_tag=selected_tag,
        confession_posts=confession_posts,
        confession_tag=confession_tag
    )


@public_bp.route('/posts/<int:post_id>')
def post_detail(post_id):
    """Post detail page."""
    post = Post.query.get_or_404(post_id)
    
    # Only allow viewing published posts (unless user is author or admin)
    if post.status != PostStatus.PUBLISHED:
        if not current_user.is_authenticated:
            flash('Bài viết không tồn tại hoặc chưa được công khai', 'warning')
            return redirect(url_for('public.index'))
        
        # Check if user can view this post
        if not (current_user.is_admin() or current_user.id == post.author_id):
            flash('Bạn không có quyền xem bài viết này', 'danger')
            return redirect(url_for('public.index'))
    
    # Get comments
    comments = post.comments.filter_by(is_approved=True).order_by(Comment.created_at.desc()).all()
    
    return render_template(
        'public/post_detail.html',
        post=post,
        comments=comments
    )


@public_bp.route('/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """Add comment to post."""
    post = Post.query.get_or_404(post_id)
    
    # Only allow comments on published posts
    if post.status != PostStatus.PUBLISHED:
        flash('Không thể bình luận trên bài viết này', 'danger')
        return redirect(url_for('public.post_detail', post_id=post_id))
    
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Vui lòng nhập nội dung bình luận', 'warning')
        return redirect(url_for('public.post_detail', post_id=post_id))
    
    try:
        comment = Comment(
            post_id=post_id,
            content=content
        )
        
        if current_user.is_authenticated:
            comment.user_id = current_user.id
        else:
            # Guest comment
            guest_name = request.form.get('guest_name', '').strip()
            comment.guest_name = guest_name if guest_name else 'Khách'
        
        db.session.add(comment)
        db.session.commit()
        
        # Notify post author about new comment
        if current_user.is_authenticated:
            NotificationService.notify_post_author(comment)
        
        flash('Bình luận của bạn đã được thêm', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Lỗi khi thêm bình luận', 'danger')
    
    return redirect(url_for('public.post_detail', post_id=post_id))


@public_bp.route('/about')
def about():
    """About page."""
    return render_template('public/about.html')


@public_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('public/contact.html')


@public_bp.route('/search')
def search():
    """Search posts."""
    keyword = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if not keyword:
        flash('Vui lòng nhập từ khóa tìm kiếm', 'warning')
        return redirect(url_for('public.index'))
    
    pagination = PostService.search_posts(keyword, page=page, per_page=12)
    
    return render_template(
        'public/search.html',
        posts=pagination.items,
        pagination=pagination,
        keyword=keyword
    )
