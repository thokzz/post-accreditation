# app/__init__.py - Updated with timezone-aware context processors
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
from datetime import datetime
import pytz

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Configuration
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import blueprints here to avoid circular imports
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.admin import bp as admin_bp
    from app.forms import bp as forms_bp
    from app.api import bp as api_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(forms_bp, url_prefix='/forms')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Context processors
    @app.context_processor
    def inject_timezone_functions():
        """Inject timezone-aware functions into templates"""
        from app.utils import (format_datetime_for_user, format_date_for_user, 
                              format_time_for_user, get_user_timezone_datetime,
                              get_system_timezone)
        
        return {
            'now_user_tz': lambda: get_user_timezone_datetime(),
            'format_datetime': format_datetime_for_user,
            'format_date': format_date_for_user,
            'format_time': format_time_for_user,
            'system_timezone': lambda: get_system_timezone().zone
        }
    
    @app.context_processor
    def inject_now():
        """Legacy context processor for backward compatibility"""
        return {'now': datetime.now(pytz.UTC)}
    
    # Template filters for timezone
    @app.template_filter('user_datetime')
    def user_datetime_filter(dt):
        """Template filter to format datetime in user timezone"""
        if dt is None:
            return 'N/A'
        from app.utils import format_datetime_for_user
        return format_datetime_for_user(dt)
    
    @app.template_filter('user_date')
    def user_date_filter(dt):
        """Template filter to format date in user timezone"""
        if dt is None:
            return 'N/A'
        from app.utils import format_date_for_user
        return format_date_for_user(dt)
    
    @app.template_filter('user_time')
    def user_time_filter(dt):
        """Template filter to format time in user timezone"""
        if dt is None:
            return 'N/A'
        from app.utils import format_time_for_user
        return format_time_for_user(dt)
    
    @app.template_filter('relative_time')
    def relative_time_filter(dt):
        """Template filter to show relative time (e.g., '2 hours ago')"""
        if dt is None:
            return 'N/A'
        
        from app.utils import get_user_timezone_datetime
        now = get_user_timezone_datetime()
        user_dt = get_user_timezone_datetime(dt)
        
        diff = now - user_dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    # Health check route (fallback if API blueprint fails)
    @app.route('/health')
    def health_check():
        """Health check endpoint for Docker"""
        try:
            # Simple database check
            from app.models import User
            user_count = User.query.count()
            
            # Get system timezone
            from app.utils import get_system_timezone
            system_tz = get_system_timezone()
            
            return jsonify({
                'status': 'healthy',
                'service': 'post-accreditation',
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'local_time': datetime.now(system_tz).isoformat(),
                'timezone': system_tz.zone,
                'database': 'connected',
                'users': user_count
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'service': 'post-accreditation',
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'error': str(e)
            }), 500
    
    return app