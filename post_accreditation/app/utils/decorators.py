from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user
from app.models import AuditLog

def anonymous_required(f):
    """Decorator to require user to be anonymous (not logged in)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            if isinstance(roles, str):
                required_roles = [roles]
            else:
                required_roles = roles
            
            if not current_user.can_access(required_roles):
                AuditLog.log_security_event(
                    action='unauthorized_access_attempt',
                    user=current_user,
                    description=f"User {current_user.username} attempted to access {request.endpoint} without proper role",
                    additional_data={
                        'required_roles': required_roles,
                        'user_role': current_user.role,
                        'endpoint': request.endpoint
                    },
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string,
                    risk_level='medium'
                )
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require administrator role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.has_role('administrator'):
            AuditLog.log_security_event(
                action='admin_access_denied',
                user=current_user,
                description=f"Non-admin user {current_user.username} attempted to access admin function",
                additional_data={
                    'endpoint': request.endpoint,
                    'user_role': current_user.role
                },
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                risk_level='high'
            )
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def audit_action(action, resource_type=None, description=None):
    """Decorator to automatically audit actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Log successful action
                AuditLog.log_action(
                    action=action,
                    user_id=current_user.id if current_user.is_authenticated else None,
                    resource_type=resource_type,
                    description=description or f"Action {action} executed successfully",
                    success=True,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string,
                    method=request.method,
                    endpoint=request.endpoint
                )
                
                return result
                
            except Exception as e:
                # Log failed action
                AuditLog.log_action(
                    action=action,
                    user_id=current_user.id if current_user.is_authenticated else None,
                    resource_type=resource_type,
                    description=description or f"Action {action} failed",
                    success=False,
                    error_message=str(e),
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string,
                    method=request.method,
                    endpoint=request.endpoint,
                    risk_level='medium'
                )
                raise
        
        return decorated_function
    return decorator

def rate_limit(max_requests=60, window=3600):
    """Simple rate limiting decorator (in production, use Redis-based solution)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For production, implement proper rate limiting with Redis
            # This is a simple placeholder
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_session(f):
    """Decorator to validate session integrity"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # Additional session validation can be added here
            # For example, checking session age, IP consistency, etc.
            pass
        
        return f(*args, **kwargs)
    return decorated_function
