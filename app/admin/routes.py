# app/admin/routes.py - Updated to use EXTERNAL_URL from config
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.admin import bp
from app.models import User, FormLink, SystemSettings, UserRole, AuditLog, FormSubmission
from app.admin.forms import UserForm, FormLinkForm, SettingsForm, ApprovalForm
from app.utils import generate_random_string, hash_password, log_audit_event
from app import db, mail
from flask_mail import Message
from datetime import datetime, timezone
from sqlalchemy import desc
import functools

def admin_required(f):
    @functools.wraps(f)
    def admin_decorated_function(*args, **kwargs):
        if current_user.role != UserRole.ADMINISTRATOR:
            flash('Administrator access required', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return admin_decorated_function

def manager_required(f):
    @functools.wraps(f)
    def manager_decorated_function(*args, **kwargs):
        if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.MANAGER]:
            flash('Manager access required', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return manager_decorated_function

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=UserRole(form.role.data),
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        log_audit_event(
            user_id=current_user.id,
            action='create_user',
            resource_type='User',
            resource_id=user.id,
            details={'username': user.username, 'role': user.role.value}
        )
        
        flash(f'User {user.username} created successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='Add User')

@bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = UserRole(form.role.data)
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        
        log_audit_event(
            user_id=current_user.id,
            action='update_user',
            resource_type='User',
            resource_id=user.id,
            details={'username': user.username, 'role': user.role.value}
        )
        
        flash(f'User {user.username} updated successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)

@bp.route('/form-links')
@login_required
@manager_required
def form_links():
    page = request.args.get('page', 1, type=int)
    links = FormLink.query.order_by(desc(FormLink.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/form_links.html', links=links)

@bp.route('/form-link/generate', methods=['GET', 'POST'])
@login_required
@manager_required
def generate_form_link():
    form = FormLinkForm()
    if form.validate_on_submit():
        token = generate_random_string(32)
        password = form.password.data
        password_hash = hash_password(password)
        
        form_link = FormLink(
            unique_token=token,
            password=password_hash,
            generator_id=current_user.id
        )
        
        db.session.add(form_link)
        db.session.commit()
        
        # Generate the full URL using EXTERNAL_URL from config
        external_url = current_app.config.get('EXTERNAL_URL', request.host_url.rstrip('/'))
        form_url = f"{external_url}{url_for('forms.form_access', token=token)}"
        
        log_audit_event(
            user_id=current_user.id,
            action='generate_form_link',
            resource_type='FormLink',
            resource_id=form_link.id,
            details={'token': token, 'external_url': external_url}
        )
        
        flash('Form link generated successfully', 'success')
        return render_template('admin/form_link_success.html', 
                             form_url=form_url, password=password, token=token)
    
    return render_template('admin/form_link_form.html', form=form)

@bp.route('/approvals')
@login_required
def approvals():
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.APPROVER]:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    submissions = FormSubmission.query.filter_by(status='pending').order_by(
        desc(FormSubmission.submitted_at)
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/approvals.html', submissions=submissions)

@bp.route('/approve/<int:id>', methods=['GET', 'POST'])
@login_required
def approve_submission(id):
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.APPROVER]:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    
    submission = FormSubmission.query.get_or_404(id)
    form = ApprovalForm()
    
    if form.validate_on_submit():
        from app.models import Approval
        
        approval = Approval(
            submission_id=submission.id,
            approver_id=current_user.id,
            status=form.status.data,
            comments=form.comments.data
        )
        
        submission.status = form.status.data
        
        db.session.add(approval)
        db.session.commit()
        
        # Send notification email (placeholder)
        if form.status.data == 'approved':
            # Send approval notification
            pass
        
        log_audit_event(
            user_id=current_user.id,
            action=f'submission_{form.status.data}',
            resource_type='FormSubmission',
            resource_id=submission.id,
            details={'status': form.status.data, 'comments': form.comments.data}
        )
        
        flash(f'Submission {form.status.data} successfully', 'success')
        return redirect(url_for('admin.approvals'))
    
    return render_template('admin/approval_form.html', form=form, submission=submission)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    form = SettingsForm()
    
    # Load current settings
    settings = {s.key: s.value for s in SystemSettings.query.all()}
    
    if form.validate_on_submit():
        # Update SMTP settings
        smtp_settings = [
            ('MAIL_SERVER', form.mail_server.data),
            ('MAIL_PORT', str(form.mail_port.data)),
            ('MAIL_USE_TLS', str(form.mail_use_tls.data)),
            ('MAIL_USERNAME', form.mail_username.data),
            ('MAIL_PASSWORD', form.mail_password.data),
            ('TIMEZONE', form.timezone.data)
        ]
        
        for key, value in smtp_settings:
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_by = current_user.id
                setting.updated_at = datetime.now(timezone.utc)
            else:
                setting = SystemSettings(key=key, value=value, updated_by=current_user.id)
                db.session.add(setting)
        
        db.session.commit()
        
        log_audit_event(
            user_id=current_user.id,
            action='update_settings',
            details={'updated_settings': [s[0] for s in smtp_settings]}
        )
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin.settings'))
    
    # Populate form with current settings
    if settings:
        form.mail_server.data = settings.get('MAIL_SERVER', '')
        form.mail_port.data = int(settings.get('MAIL_PORT', 587))
        form.mail_use_tls.data = settings.get('MAIL_USE_TLS', 'True') == 'True'
        form.mail_username.data = settings.get('MAIL_USERNAME', '')
        form.timezone.data = settings.get('TIMEZONE', 'Asia/Manila')
    
    return render_template('admin/settings.html', form=form)

@bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(desc(AuditLog.created_at)).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/audit_logs.html', logs=logs)