"""Authentication middleware and decorators."""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user
from app.models.user import UserRole


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def member_or_admin_required(f):
    """Decorator to require member or admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
            return redirect(url_for('auth.login'))
        if not (current_user.is_member() or current_user.is_admin()):
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def active_user_required(f):
    """Decorator to require active user status."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_active_user():
            flash('Tài khoản của bạn đã bị vô hiệu hóa.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
