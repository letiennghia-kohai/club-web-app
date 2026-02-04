"""Flask application factory."""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'warning'
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create upload directories
    create_directories(app)
    
    # Register template filters (must be before CLI commands)
    register_template_filters(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Register CLI commands
    register_commands(app)
    
    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.member import member_bp
    from app.blueprints.post import post_bp
    from app.blueprints.public import public_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(member_bp, url_prefix='/member')
    app.register_blueprint(post_bp, url_prefix='/posts')


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500


def setup_logging(app):
    """Configure application logging."""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler for all logs
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=10240000,
            backupCount=5
        )
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('CLB Karate Bách Khoa startup')


def create_directories(app):
    """Create necessary directories."""
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
        # Create subdirectories
        os.makedirs(os.path.join(upload_folder, 'images'), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'videos'), exist_ok=True)


def register_template_filters(app):
    """Register custom Jinja2 template filters."""
    from app.utils.helpers import markdown_to_html, format_datetime, truncate_text
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convert markdown to HTML."""
        return markdown_to_html(text)
    
    @app.template_filter('datetime')
    def datetime_filter(value, format='%d/%m/%Y %H:%M'):
        """Format datetime."""
        return format_datetime(value, format)
    
    @app.template_filter('truncate_words')
    def truncate_words_filter(text, length=50):
        """Truncate text to specified length."""
        return truncate_text(text, length)


def register_context_processors(app):
    """Register template context processors."""
    from app.utils.helpers import get_belt_color_class
    from app.models.user import BELT_ORDER
    
    @app.context_processor
    def utility_processor():
        """Make utility functions available in all templates."""
        return {
            'get_belt_color_class': get_belt_color_class,
            'BELT_ORDER': BELT_ORDER
        }


def register_commands(app):
    """Register custom CLI commands."""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command()
    def seed_db():
        """Seed the database with initial data."""
        from app.utils.seed import seed_data
        seed_data()
        print('Database seeded successfully.')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    from app.models.user import User
    return User.query.get(int(user_id))
