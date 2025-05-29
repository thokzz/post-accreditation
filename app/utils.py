# app/utils.py - Updated with timezone awareness
import os
import secrets
import string
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import hashlib
from datetime import datetime
import pytz

def generate_random_string(length=32):
    """Generate a random string for tokens and passwords."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, upload_type='general'):
    """Save uploaded file and return the filename."""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{generate_random_string(8)}{ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_type)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        return unique_filename, file_path
    return None, None

def get_system_timezone():
    """Get the system timezone from settings."""
    try:
        from app.models import SystemSettings
        timezone_setting = SystemSettings.query.filter_by(key='TIMEZONE').first()
        if timezone_setting and timezone_setting.value:
            return pytz.timezone(timezone_setting.value)
    except:
        pass
    
    # Fallback to app config or default
    timezone_str = current_app.config.get('TIMEZONE', 'Asia/Manila')
    return pytz.timezone(timezone_str)

def get_user_timezone_datetime(dt=None):
    """Convert datetime to user's timezone-aware datetime."""
    if dt is None:
        dt = datetime.now(pytz.UTC)
    
    # If datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    # Convert to system timezone
    system_tz = get_system_timezone()
    return dt.astimezone(system_tz)

def format_datetime_for_user(dt):
    """Format datetime for display to user in their timezone."""
    if dt is None:
        return 'N/A'
    
    user_dt = get_user_timezone_datetime(dt)
    return user_dt.strftime('%Y-%m-%d %H:%M:%S %Z')

def format_date_for_user(dt):
    """Format date for display to user in their timezone."""
    if dt is None:
        return 'N/A'
    
    user_dt = get_user_timezone_datetime(dt)
    return user_dt.strftime('%Y-%m-%d')

def format_time_for_user(dt):
    """Format time for display to user in their timezone."""
    if dt is None:
        return 'N/A'
    
    user_dt = get_user_timezone_datetime(dt)
    return user_dt.strftime('%H:%M:%S %Z')

def get_timezone_aware_datetime(dt=None, timezone_str=None):
    """Convert datetime to timezone-aware datetime (legacy function for backward compatibility)."""
    if timezone_str:
        target_tz = pytz.timezone(timezone_str)
    else:
        target_tz = get_system_timezone()
    
    if dt is None:
        return datetime.now(target_tz)
    
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    return dt.astimezone(target_tz)

def hash_password(password):
    """Hash password using SHA-256 (for form link passwords)."""
    return hashlib.sha256(password.encode()).hexdigest()

def log_audit_event(user_id, action, resource_type=None, resource_id=None, details=None, ip_address=None, user_agent=None):
    """Log audit event to database with timezone awareness."""
    from app.models import AuditLog
    from app import db
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(pytz.UTC)  # Always store in UTC
    )
    db.session.add(audit_log)
    db.session.commit()