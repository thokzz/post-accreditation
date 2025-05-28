# app/utils.py
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

def get_timezone_aware_datetime(dt=None, timezone_str='Asia/Manila'):
    """Convert datetime to timezone-aware datetime."""
    if dt is None:
        dt = datetime.utcnow()
    
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    target_tz = pytz.timezone(timezone_str)
    return dt.astimezone(target_tz)

def hash_password(password):
    """Hash password using SHA-256 (for form link passwords)."""
    return hashlib.sha256(password.encode()).hexdigest()

def log_audit_event(user_id, action, resource_type=None, resource_id=None, details=None, ip_address=None, user_agent=None):
    """Log audit event to database."""
    from app.models import AuditLog
    from app import db
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.session.add(audit_log)
    db.session.commit()
