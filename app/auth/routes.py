import logging
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm, TwoFactorForm
from app.utils import log_audit_event
from app import db
from datetime import datetime, timezone

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    logger.debug("Entering login route")
    if current_user.is_authenticated:
        logger.debug("Redirecting to main.dashboard")
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            if user.totp_enabled:
                session['pre_2fa_user_id'] = user.id
                logger.debug("Redirecting to auth.two_factor")
                return redirect(url_for('auth.two_factor'))
            else:
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                log_audit_event(
                    user_id=user.id,
                    action='login',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.dashboard')
                logger.debug(f"Redirecting to {next_page}")
                return redirect(next_page)
        flash('Invalid username or password', 'error')
        logger.debug("Flashing error: Invalid username or password")
    
    logger.debug("Rendering auth/login.html")
    return render_template('auth/login.html', form=form)
@bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    if 'pre_2fa_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    form = TwoFactorForm()
    if form.validate_on_submit():
        user = User.query.get(session['pre_2fa_user_id'])
        if user and user.verify_totp(form.token.data):
            session.pop('pre_2fa_user_id', None)
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            log_audit_event(
                user_id=user.id,
                action='login_2fa',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid authentication code', 'error')
    
    return render_template('auth/two_factor.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    log_audit_event(
        user_id=current_user.id,
        action='logout',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
