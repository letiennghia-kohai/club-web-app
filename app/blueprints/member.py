"""Member blueprint."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.middleware import login_required
from app.models.post import Post, PostStatus
from app.services.post_service import PostService
from app.services.user_service import UserService
from app.services.media_service import MediaService
from datetime import date

member_bp = Blueprint('member', __name__)


@member_bp.route('/dashboard')
@login_required
def dashboard():
    """Member dashboard."""
    # Get user's posts
    user_posts = PostService.get_user_posts(current_user.id, include_all=True)
    
    # Count by status
    draft_count = sum(1 for p in user_posts if p.status == PostStatus.DRAFT)
    pending_count = sum(1 for p in user_posts if p.status == PostStatus.PENDING_APPROVAL)
    published_count = sum(1 for p in user_posts if p.status == PostStatus.PUBLISHED)
    rejected_count = sum(1 for p in user_posts if p.status == PostStatus.REJECTED)
    
    return render_template(
        'member/dashboard.html',
        posts=user_posts[:10],  # Show recent 10
        stats={
            'draft': draft_count,
            'pending': pending_count,
            'published': published_count,
            'rejected': rejected_count
        }
    )


@member_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit profile."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        student_id = request.form.get('student_id', '').strip()
        
        # Handle avatar upload
        avatar_file = request.files.get('avatar')
        remove_avatar = request.form.get('remove_avatar') == '1'
        
        # Update avatar if needed
        if remove_avatar and current_user.avatar:
            MediaService.delete_avatar(current_user.avatar)
            current_user.avatar = None
        elif avatar_file and avatar_file.filename:
            # Delete old avatar
            if current_user.avatar:
                MediaService.delete_avatar(current_user.avatar)
            
            # Upload new avatar
            new_avatar, error = MediaService.upload_avatar(avatar_file, current_user.id)
            if error:
                flash(error, 'danger')
            else:
                current_user.avatar = new_avatar
                # Commit avatar change immediately
                db.session.commit()
        
        # Members can only update limited fields
        user, error = UserService.update_user(
            current_user.id,
            full_name=full_name,
            email=email if email else None,
            student_id=student_id if student_id else None
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Thông tin cá nhân đã được cập nhật', 'success')
            return redirect(url_for('member.profile'))

    return render_template('member/profile.html')


@member_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password."""
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([old_password, new_password, confirm_password]):
            flash('Vui lòng điền đầy đủ thông tin', 'warning')
            return render_template('member/change_password.html')
        
        if new_password != confirm_password:
            flash('Mật khẩu mới không khớp', 'warning')
            return render_template('member/change_password.html')
        
        # Validate password strength
        from app.utils.password_validator import validate_password_strength
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            flash(error_msg, 'warning')
            return render_template('member/change_password.html')
        
        success, error = UserService.change_password(current_user.id, old_password, new_password)
        
        if error:
            flash(error, 'danger')
        else:
            flash('Mật khẩu đã được thay đổi', 'success')
            return redirect(url_for('member.dashboard'))
    
    return render_template('member/change_password.html')


@member_bp.route('/posts')
@login_required
def my_posts():
    """View my posts."""
    posts = PostService.get_user_posts(current_user.id, include_all=True)
    
    return render_template('member/posts.html', posts=posts)


@member_bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new post."""
    from app.models.tag import Tag
    from app import db
    
    # Get all tags for selection
    all_tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        action = request.form.get('action', 'draft')  # draft or submit
        
        if not title or not content:
            flash('Vui lòng nhập đầy đủ tiêu đề và nội dung', 'warning')
            return render_template('member/post_editor.html', post=None)
        
        # Determine initial status
        if action == 'submit':
            status = PostStatus.PENDING_APPROVAL
        else:
            status = PostStatus.DRAFT
        
        post, error = PostService.create_post(title, content, current_user, status)
        
        if error:
            flash(error, 'danger')
        else:
            # Handle tag selection
            tag_ids = request.form.getlist('tag_ids[]')
            if tag_ids:
                for tag_id in tag_ids:
                    try:
                        tag = Tag.query.get(int(tag_id))
                        if tag:
                            post.tags.append(tag)
                    except (ValueError, TypeError):
                        continue
                db.session.commit()
            
            if status == PostStatus.PENDING_APPROVAL:
                flash('Bài viết đã được gửi đi chờ duyệt', 'success')
            else:
                flash('Bài viết đã được lưu dưới dạng bản nháp', 'success')
            return redirect(url_for('member.edit_post', post_id=post.id))
    
    return render_template('member/post_editor.html', post=None, all_tags=all_tags)


@member_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit post."""
    post = Post.query.get_or_404(post_id)
    
    # Check permissions
    if not post.can_edit(current_user):
        flash('Bạn không có quyền chỉnh sửa bài viết này', 'danger')
        return redirect(url_for('member.my_posts'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        action = request.form.get('action', 'save')
        
        if not title or not content:
            flash('Vui lòng nhập đầy đủ tiêu đề và nội dung', 'warning')
            return render_template('member/post_editor.html', post=post)
        
        # Update content
        updated_post, error = PostService.update_post(post_id, title, content, current_user)
        
        if error:
            flash(error, 'danger')
        else:
            # Update tags
            from app.models.tag import Tag
            from app import db
            
            tag_ids = request.form.getlist('tag_ids[]')
            # Clear existing tags
            post.tags = []
            # Add selected tags
            if tag_ids:
                for tag_id in tag_ids:
                    try:
                        tag = Tag.query.get(int(tag_id))
                        if tag:
                            post.tags.append(tag)
                    except (ValueError, TypeError):
                        continue
            db.session.commit()
            # Handle action
            if action == 'submit' and post.status == PostStatus.DRAFT:
                PostService.submit_for_approval(post_id, current_user)
                flash('Bài viết đã được cập nhật và gửi đi chờ duyệt', 'success')
            else:
                flash('Bài viết đã được cập nhật', 'success')
    
    # Get all tags for selection
    from app.models.tag import Tag
    all_tags = Tag.query.order_by(Tag.name).all()
    
    return render_template('member/post_editor.html', post=post, all_tags=all_tags)


@member_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete post."""
    success, error = PostService.delete_post(post_id, current_user)
    
    if error:
        flash(error, 'danger')
    else:
        flash('Bài viết đã được xóa', 'success')
    
    return redirect(url_for('member.my_posts'))


@member_bp.route('/posts/<int:post_id>/upload-image', methods=['POST'])
@login_required
def upload_image(post_id):
    """Upload image for post."""
    post = Post.query.get_or_404(post_id)
    
    # Check permissions
    if not post.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    # Check max images
    current_images = post.media.filter_by(type='IMAGE').count()
    max_images = 5
    
    if current_images >= max_images:
        return jsonify({'success': False, 'message': f'Tối đa {max_images} ảnh'}), 400
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file'}), 400
    
    file = request.files['image']
    
    media, error = MediaService.upload_image(file, post_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'media': media.to_dict()
    })


@member_bp.route('/posts/<int:post_id>/add-video', methods=['POST'])
@login_required
def add_video(post_id):
    """Add video embed for post."""
    post = Post.query.get_or_404(post_id)
    
    # Check permissions
    if not post.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    video_url = request.form.get('video_url', '').strip()
    
    if not video_url:
        return jsonify({'success': False, 'message': 'URL không được để trống'}), 400
    
    media, error = MediaService.add_video_embed(video_url, post_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'media': media.to_dict()
    })


@member_bp.route('/media/<int:media_id>/delete', methods=['POST'])
@login_required
def delete_media(media_id):
    """Delete media."""
    from app.models.media import Media
    media = Media.query.get_or_404(media_id)
    
    # Check permissions
    if not media.post.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    success, error = MediaService.delete_media(media_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({'success': True})


@member_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete comment."""
    from app.models.comment import Comment
    from app import db
    
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    
    # Check permissions - user can delete their own comments or admins can delete any
    if not comment.can_delete(current_user):
        flash('Bạn không có quyền xóa bình luận này', 'danger')
        return redirect(url_for('public.post_detail', post_id=post_id))
    
    try:
        db.session.delete(comment)
        db.session.commit()
        flash('Bình luận đã được xóa', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Lỗi khi xóa bình luận', 'danger')
    
    return redirect(url_for('public.post_detail', post_id=post_id))

