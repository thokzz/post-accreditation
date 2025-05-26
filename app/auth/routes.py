from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, TwoFactorForm, Setup2FAForm, ForgotPasswordForm
from app.models import User, AuditLog
from app import db
from app.utils.decorators import anonymous_required
from app.utils.email import send_email
import pyotp

@bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """User login with optional 2FA"""
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'error')
                AuditLog.log_security_event(
                    action='login_attempt_inactive_account',
                    user=user,
                    description=f"Login attempt for inactive account: {user.username}",
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string,
                    risk_level='medium'
                )
                return render_template('auth/login.html', form=form)
            
            # Check if 2FA is enabled
            if user.two_fa_enabled:
                session['pre_2fa_user_id'] = user.id
                session['pre_2fa_username'] = user.username
                
                AuditLog.log_security_event(
                    action='login_2fa_required',
                    user=user,
                    description=f"2FA required for user: {user.username}",
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                
                return redirect(url_for('auth.two_factor'))
            else:
                # Login without 2FA
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                
                AuditLog.log_security_event(
                    action='login_success',
                    user=user,
                    description=f"Successful login: {user.username}",
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.dashboard')
                
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(next_page)
        else:
            # Log failed login attempt
            AuditLog.log_security_event(
                action='login_failed',
                description=f"Failed login attempt for username: {form.username.data}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                risk_level='medium'
            )
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/two-factor', methods=['GET', 'POST'])
@anonymous_required
def two_factor():
    """2FA verification"""
    if 'pre_2fa_user_id' not in session:
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('auth.login'))
    
    form = TwoFactorForm()
    user = User.query.get(session['pre_2fa_user_id'])
    
    if not user:
        session.pop('pre_2fa_user_id', None)
        session.pop('pre_2fa_username', None)
        flash('Invalid session. Please login again.', 'error')
        return redirect(url_for('auth.login'))
    
    if form.validate_on_submit():
        token = form.token.data.replace(' ', '')  # Remove spaces
        
        # Check TOTP token
        if user.verify_totp(token):
            # Successful 2FA
            session.pop('pre_2fa_user_id', None)
            session.pop('pre_2fa_username', None)
            
            login_user(user, remember=True)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            AuditLog.log_security_event(
                action='2fa_success',
                user=user,
                description=f"Successful 2FA verification: {user.username}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page)
        
        # Check backup codes
        elif user.use_backup_code(token):
            # Successful backup code usage
            session.pop('pre_2fa_user_id', None)
            session.pop('pre_2fa_username', None)
            
            login_user(user, remember=True)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            AuditLog.log_security_event(
                action='backup_code_used',
                user=user,
                description=f"Backup code used for login: {user.username}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                risk_level='medium'
            )
            
            flash('Backup code used successfully. Consider regenerating your backup codes.', 'warning')
            return redirect(url_for('main.dashboard'))
        
        else:
            # Failed 2FA
            AuditLog.log_security_event(
                action='2fa_failed',
                user=user,
                description=f"Failed 2FA verification: {user.username}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                risk_level='high'
            )
            flash('Invalid verification code.', 'error')
    
    return render_template('auth/two_factor.html', form=form, username=user.username)

@bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Setup 2FA for user account"""
    if current_user.two_fa_enabled:
        flash('Two-factor authentication is already enabled.', 'info')
        return redirect(url_for('main.profile'))
    
    form = Setup2FAForm()
    
    if request.method == 'GET':
        # Generate secret and QR code
        current_user.generate_totp_secret()
        db.session.commit()
    
    if form.validate_on_submit():
        token = form.token.data.replace(' ', '')
        
        if current_user.verify_totp(token):
            current_user.enable_2fa()
            backup_codes = current_user.get_backup_codes()
            db.session.commit()
            
            AuditLog.log_security_event(
                action='2fa_enabled',
                user=current_user,
                description=f"2FA enabled for user: {current_user.username}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            flash('Two-factor authentication has been enabled successfully!', 'success')
            return render_template('auth/backup_codes.html', backup_codes=backup_codes)
        else:
            flash('Invalid verification code. Please try again.', 'error')
    
    qr_code = current_user.generate_qr_code()
    return render_template('auth/setup_2fa.html', form=form, qr_code=qr_code, 
                          secret=current_user.totp_secret)

@bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA for user account"""
    if not current_user.two_fa_enabled:
        flash('Two-factor authentication is not enabled.', 'info')
        return redirect(url_for('main.profile'))
    
    current_user.disable_2fa()
    db.session.commit()
    
    AuditLog.log_security_event(
        action='2fa_disabled',
        user=current_user,
        description=f"2FA disabled for user: {current_user.username}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        risk_level='medium'
    )
    
    flash('Two-factor authentication has been disabled.', 'warning')
    return redirect(url_for('main.profile'))

@bp.route('/regenerate-backup-codes', methods=['POST'])
@login_required
def regenerate_backup_codes():
    """Regenerate backup codes"""
    if not current_user.two_fa_enabled:
        flash('Two-factor authentication is not enabled.', 'error')
        return redirect(url_for('main.profile'))
    
    backup_codes = current_user.generate_backup_codes()
    db.session.commit()
    
    AuditLog.log_security_event(
        action='backup_codes_regenerated',
        user=current_user,
        description=f"Backup codes regenerated for user: {current_user.username}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    flash('New backup codes have been generated.', 'success')
    return render_template('auth/backup_codes.html', backup_codes=backup_codes)

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """User registration (admin only)"""
    if not current_user.has_role('administrator'):
        flash('You do not have permission to register new users.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        AuditLog.log_user_action(
            action='user_created',
            target_user=user,
            actor_user=current_user,
            description=f"User {user.username} created by {current_user.username}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        flash(f'User {user.username} has been created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    AuditLog.log_security_event(
        action='logout',
        user=current_user,
        description=f"User logout: {current_user.username}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
@anonymous_required
def forgot_password():
    """Forgot password - send reset email"""
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate password reset token (implement token generation)
            # For now, just log the request
            AuditLog.log_security_event(
                action='password_reset_requested',
                user=user,
                description=f"Password reset requested for: {user.email}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
        
        # Always show success message to prevent email enumeration
        flash('If that email address is in our system, you will receive a password reset link.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@bp.route('/api/check-username', methods=['POST'])
def check_username():
    """API endpoint to check username availability"""
    username = request.json.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Username must be at least 3 characters'})
    
    user = User.query.filter_by(username=username).first()
    
    return jsonify({
        'available': user is None,
        'message': 'Username is available' if user is None else 'Username is already taken'
    })

@bp.route('/api/check-email', methods=['POST'])
def check_email():
    """API endpoint to check email availability"""
    email = request.json.get('email', '').strip()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    user = User.query.filter_by(email=email).first()
    
    return jsonify({
        'available': user is None,
        'message': 'Email is available' if user is None else 'Email is already registered'
    })
