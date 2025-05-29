# app/main/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, abort, current_app
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, FormSubmission, FormLink, AuditLog, UserRole, FormAttachment
from app.utils import log_audit_event
from app import db
from sqlalchemy import func, desc
import os

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    stats = {}
    
    if current_user.role in [UserRole.ADMINISTRATOR, UserRole.MANAGER]:
        stats['total_submissions'] = FormSubmission.query.count()
        stats['pending_submissions'] = FormSubmission.query.filter_by(status='pending').count()
        stats['approved_submissions'] = FormSubmission.query.filter_by(status='approved').count()
        stats['rejected_submissions'] = FormSubmission.query.filter_by(status='rejected').count()
        
        # Recent submissions
        recent_submissions = FormSubmission.query.order_by(desc(FormSubmission.submitted_at)).limit(5).all()
        
        # Active form links
        active_links = FormLink.query.filter_by(is_active=True).count()
        
        stats.update({
            'recent_submissions': recent_submissions,
            'active_links': active_links
        })
    
    if current_user.role == UserRole.APPROVER:
        stats['pending_approvals'] = FormSubmission.query.filter_by(status='pending').count()
        stats['my_approvals'] = FormSubmission.query.join(FormSubmission.approvals).filter_by(approver_id=current_user.id).count()
    
    # Recent audit logs for current user
    recent_logs = AuditLog.query.filter_by(user_id=current_user.id).order_by(desc(AuditLog.created_at)).limit(5).all()
    
    log_audit_event(
        user_id=current_user.id,
        action='dashboard_view',
        ip_address=request.remote_addr
    )
    
    return render_template('main/dashboard.html', stats=stats, recent_logs=recent_logs)

@bp.route('/submissions')
@login_required
def submissions():
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.MANAGER, UserRole.APPROVER, UserRole.VIEWER]:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = FormSubmission.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    submissions = query.order_by(desc(FormSubmission.submitted_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('main/submissions.html', submissions=submissions, status_filter=status_filter)

@bp.route('/submission/<int:id>')
@login_required
def view_submission(id):
    submission = FormSubmission.query.get_or_404(id)
    
    log_audit_event(
        user_id=current_user.id,
        action='view_submission',
        resource_type='FormSubmission',
        resource_id=id,
        ip_address=request.remote_addr
    )
    
    return render_template('main/submission_detail.html', submission=submission)

@bp.route('/attachment/<int:id>/view')
@login_required
def view_attachment(id):
    """View attachment content (for preview)"""
    attachment = FormAttachment.query.get_or_404(id)
    
    # Check if user has permission to view this attachment
    submission = attachment.submission
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.MANAGER, UserRole.APPROVER, UserRole.VIEWER]:
        abort(403)
    
    # Get file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.file_path)
    
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    # Determine content type based on file extension
    file_ext = attachment.original_filename.split('.')[-1].lower()
    content_type_map = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp'
    }
    
    content_type = content_type_map.get(file_ext, 'application/octet-stream')
    
    log_audit_event(
        user_id=current_user.id,
        action='view_attachment',
        resource_type='FormAttachment',
        resource_id=id,
        ip_address=request.remote_addr
    )
    
    return send_file(
        file_path,
        mimetype=content_type,
        as_attachment=False  # Display inline for preview
    )

@bp.route('/attachment/<int:id>/download')
@login_required
def download_attachment(id):
    """Download attachment file"""
    attachment = FormAttachment.query.get_or_404(id)
    
    # Check if user has permission to download this attachment
    submission = attachment.submission
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.MANAGER, UserRole.APPROVER, UserRole.VIEWER]:
        abort(403)
    
    # Get file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.file_path)
    
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    log_audit_event(
        user_id=current_user.id,
        action='download_attachment',
        resource_type='FormAttachment',
        resource_id=id,
        ip_address=request.remote_addr
    )
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=attachment.original_filename
    )