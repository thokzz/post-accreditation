from datetime import datetime, timezone
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from app import db
import pyotp
import qrcode
from io import BytesIO
import base64

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Enum('administrator', 'manager', 'approver', 'viewer', name='user_roles'), 
                     nullable=False, default='viewer')
    
    # 2FA fields
    totp_secret = db.Column(db.String(32))
    two_fa_enabled = db.Column(db.Boolean, default=False)
    backup_codes = db.Column(db.Text)  # JSON string of backup codes
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    created_forms = db.relationship('AccreditationForm', backref='creator', lazy='dynamic',
                                   foreign_keys='AccreditationForm.created_by')
    approvals = db.relationship('Approval', backref='approver', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def can_access(self, required_roles):
        """Check if user can access resource based on role hierarchy"""
        role_hierarchy = {
            'administrator': 4,
            'manager': 3,
            'approver': 2,
            'viewer': 1
        }
        
        if isinstance(required_roles, str):
            required_roles = [required_roles]
        
        user_level = role_hierarchy.get(self.role, 0)
        for required_role in required_roles:
            if user_level >= role_hierarchy.get(required_role, 0):
                return True
        return False
    
    # 2FA Methods
    def generate_totp_secret(self):
        """Generate TOTP secret for 2FA"""
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self, app_name="Post Accreditation"):
        """Get TOTP URI for QR code generation"""
        if not self.totp_secret:
            self.generate_totp_secret()
        
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name=app_name
        )
    
    def generate_qr_code(self):
        """Generate QR code for 2FA setup"""
        uri = self.get_totp_uri()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.totp_secret:
            return False
        
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token)
    
    def enable_2fa(self):
        """Enable 2FA for user"""
        self.two_fa_enabled = True
        self.generate_backup_codes()
    
    def disable_2fa(self):
        """Disable 2FA for user"""
        self.two_fa_enabled = False
        self.totp_secret = None
        self.backup_codes = None
    
    def generate_backup_codes(self):
        """Generate backup codes for 2FA"""
        import secrets
        import json
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.backup_codes = json.dumps(codes)
        return codes
    
    def get_backup_codes(self):
        """Get backup codes"""
        if self.backup_codes:
            import json
            return json.loads(self.backup_codes)
        return []
    
    def use_backup_code(self, code):
        """Use backup code and remove it from available codes"""
        codes = self.get_backup_codes()
        if code.upper() in codes:
            codes.remove(code.upper())
            import json
            self.backup_codes = json.dumps(codes)
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'two_fa_enabled': self.two_fa_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
