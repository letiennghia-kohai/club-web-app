"""Admin blueprint."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.middleware import admin_required
from app.models.post import Post, PostStatus
from app.models.user import User, UserRole
from app.models.comment import Comment
from app.models.media import Media
from app.services.post_service import PostService
from app.services.user_service import UserService
from app import db
from datetime import date

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard."""
    # Get statistics
    total_members = User.query.filter_by(role=UserRole.MEMBER).count()
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(status=PostStatus.PUBLISHED).count()
    pending_posts = Post.query.filter_by(status=PostStatus.PENDING_APPROVAL).count()
    total_comments = Comment.query.count()
    
    # Get recent pending posts
    recent_pending = Post.query.filter_by(
        status=PostStatus.PENDING_APPROVAL
    ).order_by(Post.created_at.desc()).limit(5).all()
    
    # Get recent members
    recent_members = User.query.filter_by(
        role=UserRole.MEMBER
    ).order_by(User.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        stats={
            'total_members': total_members,
            'total_posts': total_posts,
            'published_posts': published_posts,
            'pending_posts': pending_posts,
            'total_comments': total_comments
        },
        recent_pending=recent_pending,
        recent_members=recent_members
    )


@admin_bp.route('/posts/pending')
@admin_required
def posts_pending():
    """View pending posts."""
    pending_posts = PostService.get_pending_posts()
    
    return render_template(
        'admin/posts_pending.html',
        posts=pending_posts
    )


@admin_bp.route('/posts/<int:post_id>/approve', methods=['POST'])
@admin_required
def approve_post(post_id):
    """Approve a post."""
    post, error = PostService.approve_post(post_id, current_user)
    
    if error:
        flash(error, 'danger')
    else:
        flash(f'Bài viết "{post.title}" đã được duyệt và công khai', 'success')
    
    return redirect(url_for('admin.posts_pending'))


@admin_bp.route('/posts/<int:post_id>/reject', methods=['POST'])
@admin_required
def reject_post(post_id):
    """Reject a post."""
    reason = request.form.get('reason', '').strip()
    
    post, error = PostService.reject_post(post_id, current_user, reason)
    
    if error:
        flash(error, 'danger')
    else:
        flash(f'Bài viết "{post.title}" đã bị từ chối', 'warning')
    
    return redirect(url_for('admin.posts_pending'))


@admin_bp.route('/posts')
@admin_required
def posts_all():
    """View all posts."""
    status_filter = request.args.get('status', 'all')
    
    query = Post.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    posts = query.order_by(Post.created_at.desc()).all()
    
    return render_template(
        'admin/posts_all.html',
        posts=posts,
        current_filter=status_filter
    )


@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    """Delete a post."""
    success, error = PostService.delete_post(post_id, current_user)
    
    if error:
        flash(error, 'danger')
    else:
        flash('Bài viết đã được xóa', 'success')
    
    return redirect(url_for('admin.posts_all'))


@admin_bp.route('/users')
@admin_required
def users():
    """User management with search."""
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if search_query:
        pagination = UserService.search_users(search_query, page=page, per_page=20)
        users_list = pagination.items
    else:
        users_list = UserService.get_all_users()
        pagination = None
    
    return render_template(
        'admin/users.html',
        users=users_list,
        pagination=pagination,
        search_query=search_query
    )


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create new user."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', UserRole.MEMBER)
        student_id = request.form.get('student_id', '').strip()
        belt = request.form.get('belt', '').strip()
        join_date_str = request.form.get('join_date', '')
        
        # Parse join date
        join_date = None
        if join_date_str:
            try:
                join_date = date.fromisoformat(join_date_str)
            except:
                pass
        
        user, error = UserService.create_user(
            username=username,
            password=password,
            full_name=full_name,
            email=email if email else None,
            role=role,
            student_id=student_id if student_id else None,
            belt=belt if belt else None,
            join_date=join_date
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash(f'Người dùng "{username}" đã được tạo', 'success')
            return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', user=None)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role')
        student_id = request.form.get('student_id', '').strip()
        belt = request.form.get('belt', '').strip()
        join_date_str = request.form.get('join_date', '')
        status = request.form.get('status')
        
        # Parse join date
        join_date = None
        if join_date_str:
            try:
                join_date = date.fromisoformat(join_date_str)
            except:
                pass
        
        updated_user, error = UserService.update_user(
            user_id,
            full_name=full_name,
            email=email if email else None,
            role=role,
            student_id=student_id if student_id else None,
            belt=belt if belt else None,
            join_date=join_date,
            status=status
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Thông tin người dùng đã được cập nhật', 'success')
            return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user."""
    # Prevent deleting self
    if user_id == current_user.id:
        flash('Không thể xóa tài khoản của chính bạn', 'danger')
        return redirect(url_for('admin.users'))
    
    success, error = UserService.delete_user(user_id)
    
    if error:
        flash(error, 'danger')
    else:
        flash('Người dùng đã được xóa', 'success')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active/inactive status."""
    user, error = UserService.toggle_user_status(user_id)
    
    if error:
        flash(error, 'danger')
    else:
        status_text = 'kích hoạt' if user.is_active_user() else 'vô hiệu hóa'
        flash(f'Tài khoản đã được {status_text}', 'success')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/comments')
@admin_required
def comments():
    """View and moderate comments with search."""
    from app.services.comment_service import CommentService
    
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if search_query:
        pagination = CommentService.search_comments(search_query, page=page)
        comments_list = pagination.items
    else:
        pagination = CommentService.get_all_comments(page=page)
        comments_list = pagination.items
    
    return render_template(
        'admin/comments.html',
        comments=comments_list,
        pagination=pagination,
        search_query=search_query
    )


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@admin_required
def delete_comment(comment_id):
    """Delete comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        flash('Bình luận đã được xóa', 'success')
    except:
        db.session.rollback()
        flash('Lỗi khi xóa bình luận', 'danger')
    
    return redirect(url_for('admin.comments'))


@admin_bp.route('/posts/create', methods=['GET', 'POST'])
@admin_required
def create_post():
    """Admin creates a post (auto-published)."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        video_url = request.form.get('video_url', '').strip()
        images = request.files.getlist('images')
        
        # Create post (admin posts auto-published)
        post, error = PostService.create_post(
            title=title,
            content=content,
            author=current_user
        )
        
        if error:
            flash(error, 'danger')
            return render_template('admin/post_editor.html', post=None)
        
        # Auto-publish admin posts
        post.status = PostStatus.PUBLISHED
        post.published_at = db.func.now()
        
        # Handle images
        if images:
            from app.services.media_service import MediaService
            for image_file in images[:5]:  # Max 5 images
                if image_file.filename:
                    media, error = MediaService.upload_image(image_file, post.id)
                    if error:
                        flash(f'Lỗi upload ảnh: {error}', 'warning')
        
        # Handle video URL
        if video_url:
            from app.services.media_service import MediaService
            media, error = MediaService.add_video_embed(video_url, post.id)
            if error:
                flash(f'Lỗi embed video: {error}', 'warning')
        
        db.session.commit()
        flash(f'Bài viết "{post.title}" đã được đăng và công khai', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/post_editor.html', post=None)


@admin_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    """Admin edits a post."""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        video_url = request.form.get('video_url', '').strip()
        images = request.files.getlist('images')
        
        # Update post
        post, error = PostService.update_post(
            post_id=post_id,
            title=title,
            content=content,
            user=current_user
        )
        
        if error:
            flash(error, 'danger')
            return render_template('admin/post_editor.html', post=post)
        
        # Handle new images
        if images:
            from app.services.media_service import MediaService
            for image_file in images[:5]:
                if image_file.filename:
                    media, error = MediaService.upload_image(image_file, post.id)
                    if error:
                        flash(f'Lỗi upload ảnh: {error}', 'warning')
        
        # Handle video URL
        if video_url:
            from app.services.media_service import MediaService
            media, error = MediaService.create_video_embed(video_url, post.id)
            if error:
                flash(f'Lỗi embed video: {error}', 'warning')
        
        db.session.commit()
        flash(f'Bài viết "{post.title}" đã được cập nhật', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # Get existing images and videos
    images = post.get_media_images()
    videos = post.get_media_videos()
    
    return render_template('admin/post_editor.html', post=post, images=images, videos=videos)


@admin_bp.route('/promotions', methods=['GET'])
@admin_required
def promotions():
    """Belt promotion management page."""
    from app.models.user import BELT_ORDER, UserStatus
    
    # Get all active members grouped by belt
    users_by_belt = {}
    for belt in BELT_ORDER:
        users_by_belt[belt] = User.query.filter_by(
            role=UserRole.MEMBER,
            belt=belt,
            status=UserStatus.ACTIVE
        ).order_by(User.full_name).all()
    
    # Also get users without belt
    users_by_belt['Chưa có đai'] = User.query.filter_by(
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE
    ).filter(
        db.or_(User.belt == None, User.belt == '')
    ).order_by(User.full_name).all()
    
    return render_template(
        'admin/promotions.html',
        users_by_belt=users_by_belt,
        belt_order=BELT_ORDER
    )


@admin_bp.route('/promotions/bulk', methods=['POST'])
@admin_required
def bulk_promote():
    """Bulk promote users to new belt."""
    user_ids = request.form.getlist('user_ids[]')
    new_belt = request.form.get('new_belt')
    
    if not user_ids:
        flash('Vui lòng chọn ít nhất một võ sinh', 'warning')
        return redirect(url_for('admin.promotions'))
    
    if not new_belt:
        flash('Vui lòng chọn đai mới', 'warning')
        return redirect(url_for('admin.promotions'))
    
    # Convert to integers
    try:
        user_ids = [int(uid) for uid in user_ids]
    except ValueError:
        flash('Dữ liệu không hợp lệ', 'danger')
        return redirect(url_for('admin.promotions'))
    
    results, errors = UserService.bulk_promote_belt(user_ids, new_belt)
    
    if results:
        flash(f'Đã thăng đai cho {len(results)} võ sinh lên {new_belt}', 'success')
    
    for error in errors:
        flash(error, 'warning')
    
    return redirect(url_for('admin.promotions'))
