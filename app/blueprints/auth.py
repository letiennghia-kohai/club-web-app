"""Authentication blueprint."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, logout_user
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('member.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin', 'danger')
            return render_template('auth/login.html')
        
        success, result = AuthService.authenticate(username, password, remember)
        
        if success:
            flash(f'Chào mừng {result.full_name}!', 'success')
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if result.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('member.dashboard'))
        else:
            flash(result, 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Logout."""
    logout_user()
    flash('Bạn đã đăng xuất', 'info')
    return redirect(url_for('public.index'))
