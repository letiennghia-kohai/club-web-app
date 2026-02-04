"""Password validation utilities."""
import re

def validate_password_strength(password):
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter  
    - At least one digit
    - At least one special character
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not password:
        return False, 'Mật khẩu không được để trống'
    
    if len(password) < 8:
        return False, 'Mật khẩu phải có ít nhất 8 ký tự'
    
    if not re.search(r'[A-Z]', password):
        return False, 'Mật khẩu phải có ít nhất 1 chữ hoa'
    
    if not re.search(r'[a-z]', password):
        return False, 'Mật khẩu phải có ít nhất 1 chữ thường'
    
    if not re.search(r'\d', password):
        return False, 'Mật khẩu phải có ít nhất 1 chữ số'
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Mật khẩu phải có ít nhất 1 ký tự đặc biệt (!@#$%^&*...)'
    
    return True, None
