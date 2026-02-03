"""Authentication service."""
from flask_login import login_user, logout_user
from app.models.user import User
from flask import current_app


class AuthService:
    """Service for authentication."""
    
    @staticmethod
    def authenticate(username, password, remember=False):
        """Authenticate user with username and password."""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            current_app.logger.warning(f'Failed login attempt: username not found - {username}')
            return False, 'Tên đăng nhập hoặc mật khẩu không đúng'
        
        if not user.check_password(password):
            current_app.logger.warning(f'Failed login attempt: wrong password for user - {username}')
            return False, 'Tên đăng nhập hoặc mật khẩu không đúng'
        
        if not user.is_active_user():
            current_app.logger.warning(f'Inactive user login attempt - {username}')
            return False, 'Tài khoản đã bị vô hiệu hóa'
        
        # Log in user
        login_user(user, remember=remember)
        
        current_app.logger.info(f'User logged in: {username}')
        
        return True, user
    
    @staticmethod
    def logout():
        """Log out current user."""
        logout_user()
