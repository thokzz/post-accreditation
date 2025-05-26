from datetime import datetime, timezone
from app import db
import json
import secrets
import string

class AccreditationForm(db.Model):
    __tablename__ = 'accreditation_forms'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Unique form identifier and access
    form_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    form_password = db.Column(db.String(128), nullable=False)
    
    # Form status
    status = db.Column(db.Enum('draft', 'submitted', 'under_review', 'approved', 'rejected', 
                              name='form_status'), default='draft')
    
    # Basic company information
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    business_address = db.Column(db.Text, nullable=False)
    business_email = db.Column(db.String(120), nullable=False)
    
    # Services (JSON array)
    services_offered = db.Column(db.Text)  # JSON
    services_other = db.Column(db.String(500))
    
    # Technical specifications (JSON array)
    facility_formats = db.Column(db.Text)  # JSON
    
    # Software information (JSON objects)
    audio_software = db.Column(db.Text)  # JSON
    editing_software = db.Column(db.Text)  # JSON
    graphics_software = db.Column(db.Text)  # JSON
    
    # Staff information
    audio_engineers_count = db.Column(db.Integer, default=0)
    video_editors_count = db.Column(db.Integer, default=0)
    colorists_count = db.Column(db.Integer, default=0)
    graphics_artists_count = db.Column(db.Integer, default=0)
    animators_count = db.Column(db.Integer, default=0)
    
    # Hardware information
    total_workstations = db.Column(db.Integer, nullable=False)
    workstations_shared = db.Column(db.Enum('yes', 'no', 'mixed', name='shared_status'))
    floor_plan_file = db.Column(db.String(255))  # File path
    
    # Workstation details (JSON array)
    workstation_details = db.Column(db.Text)  # JSON
    
    # Certification
    accomplished_by = db.Column(db.String(100), nullable=False)
    signature_file = db.Column(db.String(255))  # File path
    designation = db.Column(db.String(100), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    attachments = db.relationship('FormAttachment', backref='form', lazy='dynamic', cascade='all, delete-orphan')
    approvals = db.relationship('Approval', backref='form', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AccreditationForm {self.company_name}>'
    
    @staticmethod
    def generate_form_token():
        """Generate unique form token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @staticmethod
    def generate_form_password():
        """Generate random password for form access"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    def get_form_url(self, base_url):
        """Get complete form URL with token"""
        return f"{base_url}/form/{self.form_token}"
    
    def set_services_offered(self, services_list):
        """Set services offered as JSON"""
        self.services_offered = json.dumps(services_list) if services_list else None
    
    def get_services_offered(self):
        """Get services offered from JSON"""
        if self.services_offered:
            return json.loads(self.services_offered)
        return []
    
    def set_facility_formats(self, formats_list):
        """Set facility formats as JSON"""
        self.facility_formats = json.dumps(formats_list) if formats_list else None
    
    def get_facility_formats(self):
        """Get facility formats from JSON"""
        if self.facility_formats:
            return json.loads(self.facility_formats)
        return []
    
    def set_software_data(self, software_type, software_data):
        """Set software data as JSON"""
        if software_type == 'audio':
            self.audio_software = json.dumps(software_data) if software_data else None
        elif software_type == 'editing':
            self.editing_software = json.dumps(software_data) if software_data else None
        elif software_type == 'graphics':
            self.graphics_software = json.dumps(software_data) if software_data else None
    
    def get_software_data(self, software_type):
        """Get software data from JSON"""
        software_field = getattr(self, f'{software_type}_software', None)
        if software_field:
            return json.loads(software_field)
        return []
    
    def set_workstation_details(self, workstations_data):
        """Set workstation details as JSON"""
        self.workstation_details = json.dumps(workstations_data) if workstations_data else None
    
    def get_workstation_details(self):
        """Get workstation details from JSON"""
        if self.workstation_details:
            return json.loads(self.workstation_details)
        return []
    
    def submit_form(self):
        """Submit the form and change status"""
        self.status = 'submitted'
        self.submitted_at = datetime.now(timezone.utc)
    
    def get_current_approval(self):
        """Get current approval record"""
        return self.approvals.filter_by(is_current=True).first()
    
    def can_be_edited(self):
        """Check if form can be edited"""
        return self.status in ['draft', 'submitted']
    
    def is_approved(self):
        """Check if form is approved"""
        return self.status == 'approved'
    
    def is_rejected(self):
        """Check if form is rejected"""
        return self.status == 'rejected'
    
    def to_dict(self, include_sensitive=False):
        """Convert form to dictionary"""
        data = {
            'id': self.id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'contact_number': self.contact_number,
            'contact_email': self.contact_email,
            'business_address': self.business_address,
            'business_email': self.business_email,
            'status': self.status,
            'services_offered': self.get_services_offered(),
            'services_other': self.services_other,
            'facility_formats': self.get_facility_formats(),
            'audio_software': self.get_software_data('audio'),
            'editing_software': self.get_software_data('editing'),
            'graphics_software': self.get_software_data('graphics'),
            'audio_engineers_count': self.audio_engineers_count,
            'video_editors_count': self.video_editors_count,
            'colorists_count': self.colorists_count,
            'graphics_artists_count': self.graphics_artists_count,
            'animators_count': self.animators_count,
            'total_workstations': self.total_workstations,
            'workstations_shared': self.workstations_shared,
            'workstation_details': self.get_workstation_details(),
            'accomplished_by': self.accomplished_by,
            'designation': self.designation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data.update({
                'form_token': self.form_token,
                'form_password': self.form_password
            })
        
        return data


class FormAttachment(db.Model):
    __tablename__ = 'form_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('accreditation_forms.id'), nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Attachment type/category
    attachment_type = db.Column(db.String(50))  # 'software_proof', 'floor_plan', 'signature', etc.
    attachment_category = db.Column(db.String(50))  # 'audio', 'editing', 'graphics', etc.
    
    # Additional metadata
    description = db.Column(db.String(500))
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<FormAttachment {self.original_filename}>'
    
    def to_dict(self):
        """Convert attachment to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'attachment_type': self.attachment_type,
            'attachment_category': self.attachment_category,
            'description': self.description,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
