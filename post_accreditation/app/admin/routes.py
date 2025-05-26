from datetime import datetime, timezone, timedelta
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app.admin import bp
from app.models import User, AccreditationForm, Approval, AuditLog, SystemConfiguration
from app.main.forms import ApprovalForm
from app.auth.forms import RegistrationForm
from app import db
from app.utils.decorators import role_required, admin_required
from app.utils.pdf_generator import generate_accreditation_pdf, generate_form_summary_pdf
from app.utils.email import (send_form_approved_notification, send_form_rejected_notification, 
                            send_form_revision_notification, send_welcome_email)
import io
import os
import pytz
import sys
import flask

@bp.route('/dashboard')
@login_required
@role_required(['administrator', 'manager', 'approver'])
def dashboard():
    """Admin dashboard with statistics"""
    
    # Get statistics
    total_forms = AccreditationForm.query.count()
    pending_approvals = AccreditationForm.query.filter_by(status='submitted').count()
    approved_forms = AccreditationForm.query.filter_by(status='approved').count()
    rejected_forms = AccreditationForm.query.filter_by(status='rejected').count()
    
    # Recent activity
    recent_forms = AccreditationForm.query.order_by(desc(AccreditationForm.created_at)).limit(10).all()
    recent_approvals = Approval.query.filter(Approval.reviewed_at.isnot(None))\
                              .order_by(desc(Approval.reviewed_at)).limit(10).all()
    
    # Forms by status for chart
    status_counts = db.session.query(
        AccreditationForm.status, 
        func.count(AccreditationForm.id)
    ).group_by(AccreditationForm.status).all()
    
    # Forms created in last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_submissions = db.session.query(
        func.date(AccreditationForm.created_at),
        func.count(AccreditationForm.id)
    ).filter(AccreditationForm.created_at >= thirty_days_ago)\
     .group_by(func.date(AccreditationForm.created_at)).all()
    
    return render_template('admin/dashboard.html',
                         total_forms=total_forms,
                         pending_approvals=pending_approvals,
                         approved_forms=approved_forms,
                         rejected_forms=rejected_forms,
                         recent_forms=recent_forms,
                         recent_approvals=recent_approvals,
                         status_counts=status_counts,
                         recent_submissions=recent_submissions)

@bp.route('/forms')
@login_required
@role_required(['administrator', 'manager', 'approver'])
def forms():
    """List all forms with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    query = AccreditationForm.query
    
    # Apply filters based on user role
    if current_user.has_role('approver') and not current_user.can_access(['manager', 'administrator']):
        # Approvers only see submitted forms or forms they've reviewed
        query = query.filter(
            db.or_(
                AccreditationForm.status == 'submitted',
                AccreditationForm.approvals.any(Approval.approver_id == current_user.id)
            )
        )
    elif current_user.has_role('manager') and not current_user.has_role('administrator'):
        # Managers only see forms they created
        query = query.filter(AccreditationForm.created_by == current_user.id)
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter(AccreditationForm.status == status_filter)
    
    # Apply search filter
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                AccreditationForm.company_name.ilike(search_term),
                AccreditationForm.contact_person.ilike(search_term),
                AccreditationForm.contact_email.ilike(search_term)
            )
        )
    
    forms = query.order_by(desc(AccreditationForm.created_at)).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    
    return render_template('admin/forms.html', forms=forms, 
                          status_filter=status_filter, search=search)

@bp.route('/forms/<int:form_id>')
@login_required
@role_required(['administrator', 'manager', 'approver'])
def view_form(form_id):
    """View detailed form information"""
    form = AccreditationForm.query.get_or_404(form_id)
    
    # Check permissions
    if current_user.has_role('manager') and not current_user.has_role('administrator'):
        if form.created_by != current_user.id:
            flash('You do not have permission to view this form.', 'error')
            return redirect(url_for('admin.forms'))
    
    approval_form = ApprovalForm()
    current_approval = form.get_current_approval()
    
    return render_template('admin/view_form.html', form=form, 
                          approval_form=approval_form, current_approval=current_approval)

@bp.route('/forms/<int:form_id>/approve', methods=['POST'])
@login_required
@role_required(['approver', 'administrator'])
def process_approval(form_id):
    """Process form approval/rejection"""
    form = AccreditationForm.query.get_or_404(form_id)
    approval_form = ApprovalForm()
    
    if approval_form.validate_on_submit():
        # Get or create approval record
        approval = Approval.query.filter_by(form_id=form_id, is_current=True).first()
        if not approval:
            approval = Approval(
                form_id=form_id,
                approver_id=current_user.id,
                is_current=True
            )
            db.session.add(approval)
        
        action = approval_form.action.data
        comments = approval_form.comments.data
        internal_notes = approval_form.internal_notes.data
        
        # Process the action
        if action == 'approve':
            approval.approve(comments, internal_notes)
            send_form_approved_notification(form, approval)
            flash(f'Form for {form.company_name} has been approved.', 'success')
            
        elif action == 'reject':
            approval.reject(comments, internal_notes)
            send_form_rejected_notification(form, approval)
            flash(f'Form for {form.company_name} has been rejected.', 'warning')
            
        elif action == 'needs_revision':
            approval.request_revision(comments, internal_notes)
            send_form_revision_notification(form, approval)
            flash(f'Revision requested for {form.company_name}.', 'info')
        
        # Log the approval action
        AuditLog.log_approval_action(
            action=f'form_{action}',
            approval=approval,
            user=current_user,
            description=f"Form {action} by {current_user.username}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.commit()
        
    else:
        for field, errors in approval_form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('admin.view_form', form_id=form_id))

@bp.route('/forms/<int:form_id>/pdf')
@login_required
@role_required(['administrator', 'manager', 'approver'])
def download_form_pdf(form_id):
    """Download form as PDF"""
    form = AccreditationForm.query.get_or_404(form_id)
    
    # Check permissions
    if current_user.has_role('manager') and not current_user.has_role('administrator'):
        if form.created_by != current_user.id:
            flash('You do not have permission to download this form.', 'error')
            return redirect(url_for('admin.forms'))
    
    # Generate PDF
    pdf_buffer = generate_accreditation_pdf(form)
    
    # Log the download
    AuditLog.log_form_action(
        action='pdf_downloaded',
        form=form,
        user=current_user,
        description=f"PDF downloaded for {form.company_name}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    filename = f"accreditation_form_{form.company_name.replace(' ', '_')}_{form.id}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@bp.route('/forms/export')
@login_required
@role_required(['administrator', 'manager'])
def export_forms():
    """Export forms summary as PDF"""
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    query = AccreditationForm.query
    
    # Apply filters
    if current_user.has_role('manager') and not current_user.has_role('administrator'):
        query = query.filter(AccreditationForm.created_by == current_user.id)
    
    if status_filter != 'all':
        query = query.filter(AccreditationForm.status == status_filter)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                AccreditationForm.company_name.ilike(search_term),
                AccreditationForm.contact_person.ilike(search_term),
                AccreditationForm.contact_email.ilike(search_term)
            )
        )
    
    forms = query.order_by(desc(AccreditationForm.created_at)).all()
    
    # Generate PDF
    pdf_buffer = generate_form_summary_pdf(forms)
    
    # Log the export
    AuditLog.log_action(
        action='forms_exported',
        user_id=current_user.id,
        resource_type='forms',
        description=f"Forms summary exported by {current_user.username}",
        additional_data={
            'total_forms': len(forms),
            'status_filter': status_filter,
            'search': search
        },
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    filename = f"forms_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', 'all')
    search = request.args.get('search', '')
    
    query = User.query
    
    # Apply filters
    if role_filter != 'all':
        query = query.filter(User.role == role_filter)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    
    return render_template('admin/users.html', users=users, 
                          role_filter=role_filter, search=search)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    
    # Get user's activity
    recent_activity = AuditLog.query.filter_by(user_id=user_id)\
                                  .order_by(desc(AuditLog.timestamp)).limit(20).all()
    
    # Get user's forms (if manager)
    user_forms = []
    if user.has_role('manager'):
        user_forms = AccreditationForm.query.filter_by(created_by=user_id)\
                                          .order_by(desc(AccreditationForm.created_at)).limit(10).all()
    
    return render_template('admin/view_user.html', user=user, 
                          recent_activity=recent_activity, user_forms=user_forms)

@bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.view_user', user_id=user_id))
    
    old_status = user.is_active
    user.is_active = not user.is_active
    
    # Log the action
    AuditLog.log_user_action(
        action='user_status_changed',
        target_user=user,
        actor_user=current_user,
        description=f"User {user.username} {'activated' if user.is_active else 'deactivated'}",
        old_values={'is_active': old_status},
        new_values={'is_active': user.is_active},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('admin.view_user', user_id=user_id))

@bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """View audit logs"""
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', 'all')
    user_filter = request.args.get('user', 'all')
    risk_filter = request.args.get('risk', 'all')
    
    query = AuditLog.query
    
    # Apply filters
    if action_filter != 'all':
        query = query.filter(AuditLog.action.ilike(f'%{action_filter}%'))
    
    if user_filter != 'all':
        query = query.filter(AuditLog.user_id == user_filter)
    
    if risk_filter != 'all':
        query = query.filter(AuditLog.risk_level == risk_filter)
    
    logs = query.order_by(desc(AuditLog.timestamp)).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    
    # Get unique actions for filter
    unique_actions = db.session.query(AuditLog.action).distinct().all()
    actions = [action[0] for action in unique_actions]
    
    # Get users for filter
    users = User.query.order_by(User.username).all()
    
    return render_template('admin/audit_logs.html', logs=logs, 
                          action_filter=action_filter, user_filter=user_filter,
                          risk_filter=risk_filter, actions=actions, users=users)

@bp.route('/system-config')
@login_required
@admin_required
def system_config():
    """System configuration page"""
    configs = SystemConfiguration.query.order_by(SystemConfiguration.category, 
                                                SystemConfiguration.key).all()
    
    # Group by category
    config_groups = {}
    for config in configs:
        category = config.category or 'general'
        if category not in config_groups:
            config_groups[category] = []
        config_groups[category].append(config)
    
    return render_template('admin/system_config.html', config_groups=config_groups)

@bp.route('/system-config/update', methods=['POST'])
@login_required
@admin_required
def update_system_config():
    """Update system configuration"""
    config_id = request.form.get('config_id')
    new_value = request.form.get('value')
    
    config = SystemConfiguration.query.get_or_404(config_id)
    
    old_value = config.get_value()
    config.set_value(new_value, current_user.id)
    
    # Log the change
    AuditLog.log_action(
        action='config_updated',
        user_id=current_user.id,
        resource_type='configuration',
        resource_id=config.key,
        description=f"Configuration '{config.key}' updated",
        old_values={'value': old_value},
        new_values={'value': new_value},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    db.session.commit()
    
    flash(f'Configuration "{config.key}" has been updated.', 'success')
    return redirect(url_for('admin.system_config'))

@bp.route('/api/stats')
@login_required
@role_required(['administrator', 'manager'])
def api_stats():
    """API endpoint for dashboard statistics"""
    
    # Basic stats
    stats = {
        'total_forms': AccreditationForm.query.count(),
        'pending_forms': AccreditationForm.query.filter_by(status='submitted').count(),
        'approved_forms': AccreditationForm.query.filter_by(status='approved').count(),
        'rejected_forms': AccreditationForm.query.filter_by(status='rejected').count(),
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }
    
    # Forms by status
    status_counts = db.session.query(
        AccreditationForm.status,
        func.count(AccreditationForm.id)
    ).group_by(AccreditationForm.status).all()
    
    stats['status_breakdown'] = {status: count for status, count in status_counts}
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_activity = db.session.query(
        func.date(AccreditationForm.created_at),
        func.count(AccreditationForm.id)
    ).filter(AccreditationForm.created_at >= seven_days_ago)\
     .group_by(func.date(AccreditationForm.created_at)).all()
    
    stats['recent_activity'] = {
        str(date): count for date, count in recent_activity
    }
    
    return jsonify(stats)