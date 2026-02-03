"""User service for member management."""
from datetime import datetime
from flask import current_app
from app import db
from app.models.user import User, UserRole, UserStatus


class UserService:
    """Service for user and member management."""
    
    @staticmethod
    def create_user(username, password, full_name, email=None, role=UserRole.MEMBER, **kwargs):
        """Create a new user."""
        # Check if username exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            return None, 'Tên đăng nhập đã tồn tại'
        
        # Check if email exists
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return None, 'Email đã được sử dụng'
        
        try:
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                role=role,
                student_id=kwargs.get('student_id'),
                belt=kwargs.get('belt'),
                join_date=kwargs.get('join_date'),
                status=kwargs.get('status', UserStatus.ACTIVE)
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f'User created: {username} ({role})')
            
            return user, None
            
        except Exception as e:
            current_app.logger.error(f'Error creating user: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi tạo người dùng'
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user information."""
        user = User.query.get(user_id)
        if not user:
            return None, 'Người dùng không tồn tại'
        
        try:
            # Update allowed fields
            if 'full_name' in kwargs:
                user.full_name = kwargs['full_name']
            if 'email' in kwargs:
                # Check email uniqueness
                if kwargs['email'] != user.email:
                    existing = User.query.filter_by(email=kwargs['email']).first()
                    if existing:
                        return None, 'Email đã được sử dụng'
                user.email = kwargs['email']
            if 'belt' in kwargs:
                user.belt = kwargs['belt']
            if 'student_id' in kwargs:
                user.student_id = kwargs['student_id']
            if 'join_date' in kwargs:
                user.join_date = kwargs['join_date']
            if 'status' in kwargs and kwargs['status'] is not None:
                user.status = kwargs['status']
            if 'role' in kwargs:
                user.role = kwargs['role']
            
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            current_app.logger.error(f'Error updating user: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi cập nhật thông tin'
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password."""
        user = User.query.get(user_id)
        if not user:
            return False, 'Người dùng không tồn tại'
        
        # Verify old password
        if not user.check_password(old_password):
            return False, 'Mật khẩu cũ không đúng'
        
        try:
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            current_app.logger.info(f'Password changed for user {user_id}')
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f'Error changing password: {str(e)}')
            db.session.rollback()
            return False, 'Lỗi khi đổi mật khẩu'
    
    @staticmethod
    def delete_user(user_id):
        """Delete user."""
        user = User.query.get(user_id)
        if not user:
            return False, 'Người dùng không tồn tại'
        
        try:
            db.session.delete(user)
            db.session.commit()
            
            current_app.logger.info(f'User deleted: {user.username} (ID: {user_id})')
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f'Error deleting user: {str(e)}')
            db.session.rollback()
            return False, 'Lỗi khi xóa người dùng'
    
    @staticmethod
    def get_all_members(include_inactive=False):
        """Get all members."""
        query = User.query.filter_by(role=UserRole.MEMBER)
        
        if not include_inactive:
            query = query.filter_by(status=UserStatus.ACTIVE)
        
        return query.order_by(User.join_date.desc()).all()
    
    @staticmethod
    def get_all_users():
        """Get all users (admin function)."""
        return User.query.order_by(User.created_at.desc()).all()
    
    @staticmethod
    def search_users(query, page=1, per_page=20):
        """Search users by name, email, student ID, or username."""
        from sqlalchemy import or_
        
        if not query:
            return User.query.order_by(User.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        
        search_pattern = f'%{query}%'
        return User.query.filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.student_id.ilike(search_pattern),
                User.username.ilike(search_pattern)
            )
        ).order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def toggle_user_status(user_id):
        """Toggle user active/inactive status."""
        user = User.query.get(user_id)
        if not user:
            return None, 'Người dùng không tồn tại'
        
        try:
            user.status = UserStatus.INACTIVE if user.status == UserStatus.ACTIVE else UserStatus.ACTIVE
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            current_app.logger.error(f'Error toggling user status: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi thay đổi trạng thái'
    
    @staticmethod
    def promote_belt(user_id, new_belt):
        """Promote single user to new belt."""
        from app.models.user import BELT_ORDER
        
        user = User.query.get(user_id)
        if not user:
            return None, 'Người dùng không tồn tại'
        
        # Validate belt progression (optional - can only promote, not demote)
        if user.belt and new_belt in BELT_ORDER and user.belt in BELT_ORDER:
            old_index = BELT_ORDER.index(user.belt)
            new_index = BELT_ORDER.index(new_belt)
            if new_index <= old_index:
                return None, f'Không thể hạ đai từ {user.belt} xuống {new_belt}'
        
        try:
            old_belt = user.belt
            user.belt = new_belt
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            current_app.logger.info(f'Belt promotion: {user.username} from {old_belt} to {new_belt}')
            return user, None
            
        except Exception as e:
            current_app.logger.error(f'Error promoting belt: {str(e)}')
            db.session.rollback()
            return None, 'Lỗi khi thăng đai'
    
    @staticmethod
    def bulk_promote_belt(user_ids, new_belt):
        """Promote multiple users to new belt."""
        results = []
        errors = []
        
        for user_id in user_ids:
            user, error = UserService.promote_belt(user_id, new_belt)
            if error:
                errors.append(f'User {user_id}: {error}')
            else:
                results.append(user)
        
        return results, errors

