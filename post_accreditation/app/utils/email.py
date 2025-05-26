from flask import current_app, render_template
from flask_mail import Message
from app import mail, celery
from app.models import AuditLog
import logging

logger = logging.getLogger(__name__)

@celery.task
def send_async_email(subject, recipients, template=None, text_body=None, html_body=None, **kwargs):
    """Send email asynchronously using Celery"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        if template:
            msg.html = render_template(template, **kwargs)
            # Also create a text version by stripping HTML
            import re
            msg.body = re.sub('<[^<]+?>', '', msg.html)
        else:
            if html_body:
                msg.html = html_body
            if text_body:
                msg.body = text_body
        
        mail.send(msg)
        
        # Log successful email
        AuditLog.log_action(
            action='email_sent',
            description=f"Email sent: {subject}",
            additional_data={
                'subject': subject,
                'recipients': recipients,
                'template': template
            },
            success=True
        )
        
        logger.info(f"Email sent successfully: {subject} to {recipients}")
        return True
        
    except Exception as e:
        # Log failed email
        AuditLog.log_action(
            action='email_failed',
            description=f"Failed to send email: {subject}",
            additional_data={
                'subject': subject,
                'recipients': recipients,
                'error': str(e)
            },
            success=False,
            error_message=str(e)
        )
        
        logger.error(f"Failed to send email: {subject} to {recipients}. Error: {str(e)}")
        return False

def send_email(subject, recipients, template=None, text_body=None, html_body=None, async_send=True, **kwargs):
    """Send email (sync or async)"""
    if async_send:
        send_async_email.delay(subject, recipients, template, text_body, html_body, **kwargs)
    else:
        return send_async_email(subject, recipients, template, text_body, html_body, **kwargs)

def send_notification_email(subject, recipients, template, **kwargs):
    """Send notification email to users"""
    return send_email(
        subject=subject,
        recipients=recipients,
        template=template,
        async_send=True,
        **kwargs
    )

def send_form_submitted_notification(form):
    """Send notification when a form is submitted"""
    from app.models import User
    
    # Get all approvers
    approvers = User.query.filter_by(role='approver', is_active=True).all()
    recipients = [approver.email for approver in approvers]
    
    if recipients:
        send_notification_email(
            subject=f'New Accreditation Form Submitted - {form.company_name}',
            recipients=recipients,
            template='email/form_submitted_notification.html',
            form=form,
            form_url=f"{current_app.config.get('BASE_URL', '')}/admin/forms/{form.id}"
        )

def send_form_approved_notification(form, approval):
    """Send notification when a form is approved"""
    from app.models import User
    
    # Notify the form creator (manager)
    creator = User.query.get(form.created_by)
    if creator:
        send_notification_email(
            subject=f'Accreditation Form Approved - {form.company_name}',
            recipients=[creator.email],
            template='email/form_approved_notification.html',
            form=form,
            approval=approval,
            form_url=f"{current_app.config.get('BASE_URL', '')}/admin/forms/{form.id}"
        )
    
    # Notify the applicant
    send_notification_email(
        subject=f'Your Accreditation Application has been Approved - {form.company_name}',
        recipients=[form.contact_email],
        template='email/form_approved_applicant.html',
        form=form,
        approval=approval
    )

def send_form_rejected_notification(form, approval):
    """Send notification when a form is rejected"""
    from app.models import User
    
    # Notify the form creator (manager)
    creator = User.query.get(form.created_by)
    if creator:
        send_notification_email(
            subject=f'Accreditation Form Rejected - {form.company_name}',
            recipients=[creator.email],
            template='email/form_rejected_notification.html',
            form=form,
            approval=approval,
            form_url=f"{current_app.config.get('BASE_URL', '')}/admin/forms/{form.id}"
        )
    
    # Notify the applicant
    send_notification_email(
        subject=f'Your Accreditation Application Requires Attention - {form.company_name}',
        recipients=[form.contact_email],
        template='email/form_rejected_applicant.html',
        form=form,
        approval=approval
    )

def send_form_revision_notification(form, approval):
    """Send notification when a form needs revision"""
    from app.models import User
    
    # Notify the form creator (manager)
    creator = User.query.get(form.created_by)
    if creator:
        send_notification_email(
            subject=f'Accreditation Form Needs Revision - {form.company_name}',
            recipients=[creator.email],
            template='email/form_revision_notification.html',
            form=form,
            approval=approval,
            form_url=f"{current_app.config.get('BASE_URL', '')}/admin/forms/{form.id}"
        )
    
    # Notify the applicant
    send_notification_email(
        subject=f'Your Accreditation Application Needs Revision - {form.company_name}',
        recipients=[form.contact_email],
        template='email/form_revision_applicant.html',
        form=form,
        approval=approval
    )

def send_welcome_email(user, temporary_password=None):
    """Send welcome email to new user"""
    send_notification_email(
        subject='Welcome to Post Accreditation System',
        recipients=[user.email],
        template='email/welcome.html',
        user=user,
        temporary_password=temporary_password,
        login_url=f"{current_app.config.get('BASE_URL', '')}/auth/login"
    )

def send_password_reset_email(user, reset_token):
    """Send password reset email"""
    send_notification_email(
        subject='Password Reset Request - Post Accreditation System',
        recipients=[user.email],
        template='email/password_reset.html',
        user=user,
        reset_token=reset_token,
        reset_url=f"{current_app.config.get('BASE_URL', '')}/auth/reset-password/{reset_token}"
    )

def send_security_alert_email(user, event_type, details):
    """Send security alert email"""
    send_notification_email(
        subject=f'Security Alert - {event_type}',
        recipients=[user.email],
        template='email/security_alert.html',
        user=user,
        event_type=event_type,
        details=details
    )

def send_system_notification(recipients, subject, message, level='info'):
    """Send system-wide notification"""
    send_notification_email(
        subject=f'System Notification - {subject}',
        recipients=recipients,
        template='email/system_notification.html',
        message=message,
        level=level
    )
