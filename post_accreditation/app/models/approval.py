from datetime import datetime, timezone
from app import db

class Approval(db.Model):
    __tablename__ = 'approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('accreditation_forms.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Approval status
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'needs_revision', 
                              name='approval_status'), default='pending')
    
    # Approval details
    comments = db.Column(db.Text)
    internal_notes = db.Column(db.Text)  # Internal notes not visible to external parties
    
    # Approval workflow
    is_current = db.Column(db.Boolean, default=True)
    approval_level = db.Column(db.Integer, default=1)  # For multi-level approvals
    
    # Timestamps
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Approval {self.form.company_name} - {self.status}>'
    
    def approve(self, comments=None, internal_notes=None):
        """Approve the form"""
        self.status = 'approved'
        self.comments = comments
        self.internal_notes = internal_notes
        self.reviewed_at = datetime.now(timezone.utc)
        
        # Update form status
        self.form.status = 'approved'
    
    def reject(self, comments=None, internal_notes=None):
        """Reject the form"""
        self.status = 'rejected'
        self.comments = comments
        self.internal_notes = internal_notes
        self.reviewed_at = datetime.now(timezone.utc)
        
        # Update form status
        self.form.status = 'rejected'
    
    def request_revision(self, comments=None, internal_notes=None):
        """Request revision for the form"""
        self.status = 'needs_revision'
        self.comments = comments
        self.internal_notes = internal_notes
        self.reviewed_at = datetime.now(timezone.utc)
        
        # Update form status
        self.form.status = 'under_review'
    
    def is_pending(self):
        """Check if approval is pending"""
        return self.status == 'pending'
    
    def is_completed(self):
        """Check if approval is completed"""
        return self.status in ['approved', 'rejected']
    
    def to_dict(self, include_internal=False):
        """Convert approval to dictionary"""
        data = {
            'id': self.id,
            'form_id': self.form_id,
            'approver': {
                'id': self.approver.id,
                'name': self.approver.full_name,
                'role': self.approver.role
            },
            'status': self.status,
            'comments': self.comments,
            'approval_level': self.approval_level,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }
        
        if include_internal:
            data['internal_notes'] = self.internal_notes
        
        return data


class ApprovalHistory(db.Model):
    __tablename__ = 'approval_history'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('accreditation_forms.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Action details
    action = db.Column(db.Enum('assigned', 'approved', 'rejected', 'revision_requested', 
                              'comments_added', name='approval_actions'), nullable=False)
    
    previous_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50))
    
    comments = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Timestamps
    action_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    form = db.relationship('AccreditationForm', backref='approval_history')
    approver = db.relationship('User', backref='approval_actions')
    
    def __repr__(self):
        return f'<ApprovalHistory {self.action} by {self.approver.username}>'
    
    @staticmethod
    def log_action(form_id, approver_id, action, previous_status=None, new_status=None, 
                   comments=None, internal_notes=None):
        """Log approval action"""
        history = ApprovalHistory(
            form_id=form_id,
            approver_id=approver_id,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            comments=comments,
            internal_notes=internal_notes
        )
        db.session.add(history)
        return history
    
    def to_dict(self, include_internal=False):
        """Convert approval history to dictionary"""
        data = {
            'id': self.id,
            'action': self.action,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'comments': self.comments,
            'approver': {
                'id': self.approver.id,
                'name': self.approver.full_name,
                'role': self.approver.role
            },
            'action_at': self.action_at.isoformat() if self.action_at else None
        }
        
        if include_internal:
            data['internal_notes'] = self.internal_notes
        
        return data
