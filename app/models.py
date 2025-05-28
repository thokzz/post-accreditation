# app/models.py
from app import db, login_manager, bcrypt
from datetime import datetime, timezone
from flask_login import UserMixin
from datetime import datetime, timezone
import pyotp
import qrcode
from io import BytesIO
import base64
import enum

class UserRole(enum.Enum):
    ADMINISTRATOR = "administrator"
    MANAGER = "manager"
    APPROVER = "approver"
    VIEWER = "viewer"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = db.Column(db.Boolean, default=True)
    totp_secret = db.Column(db.String(32))
    totp_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    generated_links = db.relationship('FormLink', backref='generator', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    approvals = db.relationship('Approval', backref='approver', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_totp_secret(self):
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name="GMA Post Accreditation"
        )
    
    def get_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_totp_uri())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_totp(self, token):
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token)

class FormLink(db.Model):
    __tablename__ = 'form_links'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_token = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    generator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    used_at = db.Column(db.DateTime)
    
    # Relationships
    submissions = db.relationship('FormSubmission', backref='form_link', lazy='dynamic')

class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    form_link_id = db.Column(db.Integer, db.ForeignKey('form_links.id'), nullable=False)
    
    # Company Information
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    business_address = db.Column(db.Text, nullable=False)
    business_email = db.Column(db.String(120), nullable=False)
    
    # Services offered (JSON field)
    services_offered = db.Column(db.JSON)
    others_service = db.Column(db.String(200))
    
    # Technical specifications
    facility_formats = db.Column(db.JSON)
    
    # Software information (JSON fields)
    audio_software = db.Column(db.JSON)
    editing_software = db.Column(db.JSON)
    graphics_software = db.Column(db.JSON)
    
    # Staff information
    audio_engineers_count = db.Column(db.Integer)
    video_editors_count = db.Column(db.Integer)
    colorists_count = db.Column(db.Integer)
    graphics_artists_count = db.Column(db.Integer)
    animators_count = db.Column(db.Integer)
    
    # Hardware information
    total_workstations = db.Column(db.Integer)
    workstations_shared = db.Column(db.String(10))  # Y/N/Mixed
    workstation_details = db.Column(db.JSON)
    
    # Certification
    accomplished_by = db.Column(db.String(200), nullable=False)
    designation = db.Column(db.String(200), nullable=False)
    signature_file = db.Column(db.String(255))
    
    # Metadata
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Relationships
    attachments = db.relationship('FormAttachment', backref='submission', lazy='dynamic', cascade='all, delete-orphan')
    approvals = db.relationship('Approval', backref='submission', lazy='dynamic', cascade='all, delete-orphan')

class FormAttachment(db.Model):
    __tablename__ = 'form_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    attachment_type = db.Column(db.String(100))  # proof_of_license, floor_plan, signature, etc.
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Approval(db.Model):
    __tablename__ = 'approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # approved, rejected, pending
    comments = db.Column(db.Text)
    approved_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
