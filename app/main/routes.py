from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, current_app, abort, send_file
from flask_login import login_required, current_user
from app.main import bp
from app.main.forms import AccreditationFormSubmission, ApprovalForm
from app.models import AccreditationForm, User, Approval, AuditLog, FormAttachment
from app import db
from app.utils.decorators import role_required
from app.utils.file_handler import save_uploaded_file, allowed_file
from app.utils.pdf_generator import generate_accreditation_pdf
from app.utils.email import send_notification_email
import os

@bp.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard based on role"""
    if current_user.has_role('administrator'):
        return redirect(url_for('admin.dashboard'))
    elif current_user.has_role('manager'):
        return render_template('main/manager_dashboard.html')
    elif current_user.has_role('approver'):
        return render_template('main/approver_dashboard.html')
    else:
        return render_template('main/viewer_dashboard.html')

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    from app.auth.forms import ProfileForm, ChangePasswordForm
    
    profile_form = ProfileForm(
        original_email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email
    )
    password_form = ChangePasswordForm()
    
    return render_template('main/profile.html', 
                          profile_form=profile_form, 
                          password_form=password_form)

@bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    from app.auth.forms import ProfileForm
    
    form = ProfileForm(original_email=current_user.email)
    
    if form.validate_on_submit():
        old_values = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'email': current_user.email
        }
        
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        
        db.session.commit()
        
        AuditLog.log_user_action(
            action='profile_updated',
            target_user=current_user,
            actor_user=current_user,
            description=f"Profile updated for user: {current_user.username}",
            old_values=old_values,
            new_values={
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'email': current_user.email
            },
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        flash('Your profile has been updated successfully.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('main.profile'))

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    from app.auth.forms import ChangePasswordForm
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            AuditLog.log_security_event(
                action='password_changed',
                user=current_user,
                description=f"Password changed for user: {current_user.username}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            flash('Your password has been changed successfully.', 'success')
        else:
            flash('Current password is incorrect.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('main.profile'))

@bp.route('/forms')
@login_required
@role_required(['manager', 'administrator'])
def forms_list():
    """List all accreditation forms"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    query = AccreditationForm.query
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter(AccreditationForm.status == status_filter)
    
    if search:
        query = query.filter(
            db.or_(
                AccreditationForm.company_name.ilike(f'%{search}%'),
                AccreditationForm.contact_person.ilike(f'%{search}%'),
                AccreditationForm.contact_email.ilike(f'%{search}%')
            )
        )
    
    # If user is manager, only show forms they created
    if current_user.has_role('manager') and not current_user.has_role('administrator'):
        query = query.filter(AccreditationForm.created_by == current_user.id)
    
    forms = query.order_by(AccreditationForm.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    
    return render_template('main/forms_list.html', forms=forms, 
                          status_filter=status_filter, search=search)

@bp.route('/create-form-link', methods=['GET', 'POST'])
@login_required
@role_required(['manager', 'administrator'])
def create_form_link():
    """Create a new form link for external partners"""
    if request.method == 'POST':
        # Generate new form
        form = AccreditationForm(
            form_token=AccreditationForm.generate_form_token(),
            form_password=AccreditationForm.generate_form_password(),
            created_by=current_user.id,
            company_name='',  # Will be filled by external user
            contact_person='',
            contact_number='',
            contact_email='',
            business_address='',
            business_email='',
            total_workstations=0,
            accomplished_by='',
            designation=''
        )
        
        db.session.add(form)
        db.session.commit()
        
        AuditLog.log_form_action(
            action='form_link_created',
            form=form,
            user=current_user,
            description=f"Form link created by {current_user.username}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        form_url = form.get_form_url(request.url_root.rstrip('/'))
        
        flash('Form link created successfully!', 'success')
        return render_template('main/form_link_created.html', 
                             form=form, form_url=form_url)
    
    return render_template('main/create_form_link.html')

@bp.route('/form/<token>')
def external_form(token):
    """External form access for business partners"""
    form = AccreditationForm.query.filter_by(form_token=token).first_or_404()
    
    # Check if password is required
    if 'form_authenticated' not in session or session.get('form_token') != token:
        return render_template('main/form_password.html', token=token)
    
    # Check if form is already submitted
    if form.status != 'draft':
        return render_template('main/form_already_submitted.html', form=form)
    
    form_data = AccreditationFormSubmission()
    
    # Pre-populate form if data exists
    if form.company_name:
        form_data.company_name.data = form.company_name
        form_data.contact_person.data = form.contact_person
        form_data.contact_number.data = form.contact_number
        form_data.contact_email.data = form.contact_email
        form_data.business_address.data = form.business_address
        form_data.business_email.data = form.business_email
    
    return render_template('main/external_form.html', form=form_data, token=token)

@bp.route('/form/<token>/authenticate', methods=['POST'])
def authenticate_form(token):
    """Authenticate external form access"""
    form = AccreditationForm.query.filter_by(form_token=token).first_or_404()
    password = request.form.get('password', '').strip()
    
    if password == form.form_password:
        session['form_authenticated'] = True
        session['form_token'] = token
        
        AuditLog.log_form_action(
            action='external_form_accessed',
            form=form,
            description=f"External form accessed with token: {token}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        return redirect(url_for('main.external_form', token=token))
    else:
        AuditLog.log_security_event(
            action='external_form_auth_failed',
            description=f"Failed authentication for form token: {token}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            risk_level='medium'
        )
        flash('Invalid password. Please try again.', 'error')
        return render_template('main/form_password.html', token=token)

@bp.route('/form/<token>/submit', methods=['POST'])
def submit_external_form(token):
    """Submit external accreditation form"""
    form = AccreditationForm.query.filter_by(form_token=token).first_or_404()
    
    # Check authentication
    if 'form_authenticated' not in session or session.get('form_token') != token:
        flash('Session expired. Please authenticate again.', 'error')
        return redirect(url_for('main.external_form', token=token))
    
    # Check if form is already submitted
    if form.status != 'draft':
        flash('This form has already been submitted.', 'error')
        return render_template('main/form_already_submitted.html', form=form)
    
    form_data = AccreditationFormSubmission()
    
    if form_data.validate_on_submit():
        # Update form with submitted data
        form.company_name = form_data.company_name.data
        form.contact_person = form_data.contact_person.data
        form.contact_number = form_data.contact_number.data
        form.contact_email = form_data.contact_email.data
        form.business_address = form_data.business_address.data
        form.business_email = form_data.business_email.data
        form.accomplished_by = form_data.accomplished_by.data
        form.designation = form_data.designation.data
        
        # Handle file uploads and form data processing here
        # (Implementation continues in next part due to length)
        
        form.submit_form()
        db.session.commit()
        
        # Clear session
        session.pop('form_authenticated', None)
        session.pop('form_token', None)
        
        # Log submission
        AuditLog.log_form_action(
            action='form_submitted',
            form=form,
            description=f"Form submitted by {form.company_name}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        # Send notifications to approvers
        send_notification_email(
            subject=f'New Accreditation Form Submitted - {form.company_name}',
            template='email/form_submitted.html',
            recipients=[user.email for user in User.query.filter_by(role='approver').all()],
            form=form
        )
        
        flash('Your form has been submitted successfully!', 'success')
        return render_template('main/form_submitted.html', form=form)
    
    # Form validation failed
    for field, errors in form_data.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')
    
    return render_template('main/external_form.html', form=form_data, token=token)
