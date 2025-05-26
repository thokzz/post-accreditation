from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.api import bp
from app.models import AccreditationForm, User, Approval, AuditLog
from app.utils.decorators import role_required
from app import db
from datetime import datetime, timezone

@bp.route('/forms', methods=['GET'])
@login_required
@role_required(['administrator', 'manager', 'approver'])
def get_forms():
    """API endpoint to get forms data"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = AccreditationForm.query
    
    # Apply role-based filtering
    if current_user.has_role('manager') and not current_user.has_role('administrator'):
        query = query.filter(AccreditationForm.created_by == current_user.id)
    elif current_user.has_role('approver') and not current_user.can_access(['manager', 'administrator']):
        query = query.filter(
            db.or_(
                AccreditationForm.status == 'submitted',
                AccreditationForm.approvals.any(Approval.approver_id == current_user.id)
            )
        )
    
    # Apply filters
    if status:
        query = query.filter(AccreditationForm.status == status)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                AccreditationForm.company_name.ilike(search_term),
                AccreditationForm.contact_person.ilike(search_term),
                AccreditationForm.contact_email.ilike(search_term)
            )
        )
    
    # Paginate
    forms = query.order_by(AccreditationForm.created_at.desc()).paginate(
        page=page, per_page=min(per_page, 100), error_out=False
    )
    
    return jsonify({
        'forms': [form.to_dict() for form in forms.items],
        'total': forms.total,
        'pages': forms.pages,
        'current_page': forms.page,
        'has_next': forms.has_next,
        'has_prev': forms.has_prev
    })

@bp.route('/forms/<int:form_id>', methods=['GET'])
@login_required
@role_required(['administrator', 'manager', 'approver'])
def get_form(form_id):
    """API endpoint to get single form details"""
    form = AccreditationForm.query.get_or_404(form_id)
    
    # Check permissions
    if current_user.has_role('manager') and not current_user.has_role('administrator'):
        if form.created_by != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
    
    # Include attachments and approvals
    form_data = form.to_dict()
    form_data['attachments'] = [attachment.to_dict() for attachment in form.attachments]
    form_data['approvals'] = [approval.to_dict() for approval in form.approvals]
    
    return jsonify(form_data)

@bp.route('/forms/<int:form_id>/approve', methods=['POST'])
@login_required
@role_required(['approver', 'administrator'])
def approve_form_api(form_id):
    """API endpoint for form approval"""
    form = AccreditationForm.query.get_or_404(form_id)
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    action = data.get('action')
    comments = data.get('comments', '')
    internal_notes = data.get('internal_notes', '')
    
    if action not in ['approve', 'reject', 'needs_revision']:
        return jsonify({'error': 'Invalid action'}), 400
    
    # Get or create approval record
    approval = Approval.query.filter_by(form_id=form_id, is_current=True).first()
    if not approval:
        approval = Approval(
            form_id=form_id,
            approver_id=current_user.id,
            is_current=True
        )
        db.session.add(approval)
    
    # Process the action
    if action == 'approve':
        approval.approve(comments, internal_notes)
    elif action == 'reject':
        approval.reject(comments, internal_notes)
    elif action == 'needs_revision':
        approval.request_revision(comments, internal_notes)
    
    # Log the approval action
    AuditLog.log_approval_action(
        action=f'form_{action}',
        approval=approval,
        user=current_user,
        description=f"Form {action} via API by {current_user.username}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Form {action} successfully',
        'approval': approval.to_dict()
    })

@bp.route('/users', methods=['GET'])
@login_required
@role_required(['administrator'])
def get_users():
    """API endpoint to get users data"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    search = request.args.get('search')
    
    query = User.query
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
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
    
    # Paginate
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=min(per_page, 100), error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page,
        'has_next': users.has_next,
        'has_prev': users.has_prev
    })

@bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@role_required(['administrator'])
def get_user(user_id):
    """API endpoint to get single user details"""
    user = User.query.get_or_404(user_id)
    
    user_data = user.to_dict()
    
    # Include additional data
    user_data['forms_created'] = AccreditationForm.query.filter_by(created_by=user_id).count()
    user_data['approvals_made'] = Approval.query.filter_by(approver_id=user_id).count()
    
    return jsonify(user_data)

@bp.route('/audit-logs', methods=['GET'])
@login_required
@role_required(['administrator'])
def get_audit_logs():
    """API endpoint to get audit logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action = request.args.get('action')
    user_id = request.args.get('user_id', type=int)
    risk_level = request.args.get('risk_level')
    
    query = AuditLog.query
    
    # Apply filters
    if action:
        query = query.filter(AuditLog.action.ilike(f'%{action}%'))
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if risk_level:
        query = query.filter(AuditLog.risk_level == risk_level)
    
    # Paginate
    logs = query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=min(per_page, 100), error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page,
        'has_next': logs.has_next,
        'has_prev': logs.has_prev
    })

@bp.route('/dashboard-stats', methods=['GET'])
@login_required
@role_required(['administrator', 'manager', 'approver'])
def get_dashboard_stats():
    """API endpoint for dashboard statistics"""
    from sqlalchemy import func
    from datetime import timedelta
    
    # Basic stats
    stats = {}
    
    if current_user.can_access(['administrator', 'manager']):
        # Forms statistics
        stats['forms'] = {
            'total': AccreditationForm.query.count(),
            'submitted': AccreditationForm.query.filter_by(status='submitted').count(),
            'approved': AccreditationForm.query.filter_by(status='approved').count(),
            'rejected': AccreditationForm.query.filter_by(status='rejected').count(),
            'under_review': AccreditationForm.query.filter_by(status='under_review').count()
        }
        
        # User statistics (admin only)
        if current_user.has_role('administrator'):
            stats['users'] = {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count(),
                'administrators': User.query.filter_by(role='administrator').count(),
                'managers': User.query.filter_by(role='manager').count(),
                'approvers': User.query.filter_by(role='approver').count(),
                'viewers': User.query.filter_by(role='viewer').count()
            }
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_forms = db.session.query(
            func.date(AccreditationForm.created_at),
            func.count(AccreditationForm.id)
        ).filter(AccreditationForm.created_at >= thirty_days_ago)\
         .group_by(func.date(AccreditationForm.created_at)).all()
        
        stats['recent_activity'] = {
            str(date): count for date, count in recent_forms
        }
    
    # Approver-specific stats
    if current_user.has_role('approver'):
        pending_approvals = AccreditationForm.query.filter_by(status='submitted').count()
        my_approvals = Approval.query.filter_by(approver_id=current_user.id).count()
        
        stats['approver'] = {
            'pending_approvals': pending_approvals,
            'my_total_approvals': my_approvals
        }
    
    # Manager-specific stats
    if current_user.has_role('manager'):
        my_forms = AccreditationForm.query.filter_by(created_by=current_user.id)
        stats['manager'] = {
            'my_forms_total': my_forms.count(),
            'my_forms_pending': my_forms.filter_by(status='submitted').count(),
            'my_forms_approved': my_forms.filter_by(status='approved').count()
        }
    
    return jsonify(stats)

@bp.route('/form-token/validate', methods=['POST'])
def validate_form_token():
    """API endpoint to validate form token and password"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    token = data.get('token')
    password = data.get('password')
    
    if not token or not password:
        return jsonify({'error': 'Token and password required'}), 400
    
    form = AccreditationForm.query.filter_by(form_token=token).first()
    if not form:
        return jsonify({'error': 'Invalid token'}), 404
    
    if form.form_password != password:
        # Log failed authentication attempt
        AuditLog.log_security_event(
            action='external_form_auth_failed',
            description=f"Failed authentication for form token: {token}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            risk_level='medium'
        )
        return jsonify({'error': 'Invalid password'}), 401
    
    if form.status != 'draft':
        return jsonify({'error': 'Form already submitted'}), 409
    
    # Log successful authentication
    AuditLog.log_form_action(
        action='external_form_accessed',
        form=form,
        description=f"External form accessed with token: {token}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({
        'success': True,
        'form': {
            'id': form.id,
            'company_name': form.company_name,
            'status': form.status
        }
    })

@bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'database': db_status,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    })

@bp.route('/export/forms', methods=['POST'])
@login_required
@role_required(['administrator', 'manager'])
def export_forms_api():
    """API endpoint to export forms data"""
    data = request.get_json() or {}
    
    format_type = data.get('format', 'json')  # json, csv, or pdf
    filters = data.get('filters', {})
    
    query = AccreditationForm.query
    
    # Apply role-based filtering
    if current_user.has_role('manager') and not current_user.has_role('administrator'):
        query = query.filter(AccreditationForm.created_by == current_user.id)
    
    # Apply filters
    if filters.get('status'):
        query = query.filter(AccreditationForm.status == filters['status'])
    
    if filters.get('date_from'):
        query = query.filter(AccreditationForm.created_at >= filters['date_from'])
    
    if filters.get('date_to'):
        query = query.filter(AccreditationForm.created_at <= filters['date_to'])
    
    forms = query.all()
    
    # Log the export
    AuditLog.log_action(
        action='forms_exported_api',
        user_id=current_user.id,
        resource_type='forms',
        description=f"Forms exported via API by {current_user.username}",
        additional_data={
            'format': format_type,
            'total_forms': len(forms),
            'filters': filters
        },
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    if format_type == 'json':
        return jsonify({
            'forms': [form.to_dict() for form in forms],
            'total': len(forms),
            'exported_at': datetime.now(timezone.utc).isoformat()
        })
    
    # For CSV and PDF exports, you would implement the respective logic
    # and return appropriate file responses
    
    return jsonify({'error': 'Export format not implemented yet'}), 501

@bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@bp.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized errors"""
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@bp.errorhandler(403)
def forbidden(error):
    """Handle forbidden errors"""
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@bp.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
