from datetime import datetime, timezone
from app import db
import json

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User and session information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for anonymous actions
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(255))
    
    # Action details
    action = db.Column(db.String(100), nullable=False)  # e.g., 'form_submitted', 'user_login', 'approval_granted'
    resource_type = db.Column(db.String(50))  # e.g., 'form', 'user', 'approval'
    resource_id = db.Column(db.String(50))  # ID of the affected resource
    
    # Request details
    method = db.Column(db.String(10))  # HTTP method
    endpoint = db.Column(db.String(255))  # API endpoint or route
    
    # Action metadata
    description = db.Column(db.Text)
    old_values = db.Column(db.Text)  # JSON string of old values
    new_values = db.Column(db.Text)  # JSON string of new values
    additional_data = db.Column(db.Text)  # JSON string for any additional context
    
    # Result and status
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    # Risk assessment
    risk_level = db.Column(db.Enum('low', 'medium', 'high', 'critical', name='risk_levels'), default='low')
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id}>'
    
    @staticmethod
    def log_action(action, user_id=None, resource_type=None, resource_id=None,
                   description=None, old_values=None, new_values=None,
                   additional_data=None, success=True, error_message=None,
                   risk_level='low', ip_address=None, user_agent=None,
                   method=None, endpoint=None, session_id=None):
        """Create audit log entry"""
        
        # Convert dictionaries to JSON strings
        old_values_json = json.dumps(old_values) if old_values else None
        new_values_json = json.dumps(new_values) if new_values else None
        additional_data_json = json.dumps(additional_data) if additional_data else None
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            description=description,
            old_values=old_values_json,
            new_values=new_values_json,
            additional_data=additional_data_json,
            success=success,
            error_message=error_message,
            risk_level=risk_level,
            ip_address=ip_address,
            user_agent=user_agent,
            method=method,
            endpoint=endpoint,
            session_id=session_id
        )
        
        db.session.add(audit_log)
        return audit_log
    
    @staticmethod
    def log_form_action(action, form, user=None, description=None, additional_data=None, **kwargs):
        """Log form-related actions"""
        return AuditLog.log_action(
            action=action,
            user_id=user.id if user else None,
            resource_type='form',
            resource_id=form.id,
            description=description or f"Form {action} for {form.company_name}",
            additional_data=additional_data,
            **kwargs
        )
    
    @staticmethod
    def log_user_action(action, target_user, actor_user=None, description=None, **kwargs):
        """Log user-related actions"""
        return AuditLog.log_action(
            action=action,
            user_id=actor_user.id if actor_user else None,
            resource_type='user',
            resource_id=target_user.id,
            description=description or f"User {action} for {target_user.username}",
            **kwargs
        )
    
    @staticmethod
    def log_approval_action(action, approval, user=None, description=None, **kwargs):
        """Log approval-related actions"""
        return AuditLog.log_action(
            action=action,
            user_id=user.id if user else None,
            resource_type='approval',
            resource_id=approval.id,
            description=description or f"Approval {action} for {approval.form.company_name}",
            **kwargs
        )
    
    @staticmethod
    def log_security_event(action, user=None, description=None, risk_level='medium', **kwargs):
        """Log security-related events"""
        return AuditLog.log_action(
            action=action,
            user_id=user.id if user else None,
            resource_type='security',
            description=description,
            risk_level=risk_level,
            **kwargs
        )
    
    def get_old_values(self):
        """Get old values as dictionary"""
        if self.old_values:
            return json.loads(self.old_values)
        return {}
    
    def get_new_values(self):
        """Get new values as dictionary"""
        if self.new_values:
            return json.loads(self.new_values)
        return {}
    
    def get_additional_data(self):
        """Get additional data as dictionary"""
        if self.additional_data:
            return json.loads(self.additional_data)
        return {}
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Anonymous',
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'old_values': self.get_old_values(),
            'new_values': self.get_new_values(),
            'additional_data': self.get_additional_data(),
            'success': self.success,
            'error_message': self.error_message,
            'risk_level': self.risk_level,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'method': self.method,
            'endpoint': self.endpoint,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class SystemConfiguration(db.Model):
    __tablename__ = 'system_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    data_type = db.Column(db.Enum('string', 'integer', 'boolean', 'json', name='config_types'), default='string')
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    
    # Metadata
    is_public = db.Column(db.Boolean, default=False)  # Whether config can be accessed by non-admin users
    is_system = db.Column(db.Boolean, default=False)  # System configs that shouldn't be deleted
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    updater = db.relationship('User', backref='config_updates')
    
    def __repr__(self):
        return f'<SystemConfiguration {self.key}>'
    
    def get_value(self):
        """Get typed value"""
        if not self.value:
            return None
        
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'json':
            return json.loads(self.value)
        else:
            return self.value
    
    def set_value(self, value, user_id=None):
        """Set typed value"""
        if self.data_type == 'json':
            self.value = json.dumps(value)
        else:
            self.value = str(value)
        
        self.updated_by = user_id
        self.updated_at = datetime.now(timezone.utc)
    
    @staticmethod
    def get_config(key, default=None):
        """Get configuration value by key"""
        config = SystemConfiguration.query.filter_by(key=key).first()
        if config:
            return config.get_value()
        return default
    
    @staticmethod
    def set_config(key, value, data_type='string', description=None, category='general', 
                   is_public=False, user_id=None):
        """Set configuration value"""
        config = SystemConfiguration.query.filter_by(key=key).first()
        
        if config:
            old_value = config.get_value()
            config.set_value(value, user_id)
            
            # Log the change
            AuditLog.log_action(
                action='config_updated',
                user_id=user_id,
                resource_type='configuration',
                resource_id=key,
                description=f"Configuration '{key}' updated",
                old_values={'value': old_value},
                new_values={'value': value}
            )
        else:
            config = SystemConfiguration(
                key=key,
                data_type=data_type,
                description=description,
                category=category,
                is_public=is_public,
                updated_by=user_id
            )
            config.set_value(value, user_id)
            db.session.add(config)
            
            # Log the creation
            AuditLog.log_action(
                action='config_created',
                user_id=user_id,
                resource_type='configuration',
                resource_id=key,
                description=f"Configuration '{key}' created",
                new_values={'value': value}
            )
        
        return config
    
    def to_dict(self):
        """Convert configuration to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.get_value(),
            'data_type': self.data_type,
            'description': self.description,
            'category': self.category,
            'is_public': self.is_public,
            'is_system': self.is_system,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updater.full_name if self.updater else None
        }
