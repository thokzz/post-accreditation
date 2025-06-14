# app/admin/forms.py - Updated Admin Forms with Separate SMTP and Timezone
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, BooleanField, 
                     SubmitField, TextAreaField, IntegerField)
from wtforms.validators import DataRequired, Email, Optional, NumberRange

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    role = SelectField('Role', choices=[
        ('administrator', 'Administrator'),
        ('manager', 'Manager'),
        ('approver', 'Approver'),
        ('viewer', 'Viewer')
    ], validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save User')

class FormLinkForm(FlaskForm):
    password = StringField('Access Password', validators=[DataRequired()])
    submit = SubmitField('Generate Link')

class ApprovalForm(FlaskForm):
    status = SelectField('Decision', choices=[
        ('approved', 'Approve'),
        ('rejected', 'Reject')
    ], validators=[DataRequired()])
    comments = TextAreaField('Comments')
    submit = SubmitField('Submit Decision')

class SMTPSettingsForm(FlaskForm):
    # SMTP Settings
    mail_server = StringField('SMTP Server')
    mail_port = IntegerField('SMTP Port', validators=[Optional(), NumberRange(min=1, max=65535)])
    mail_use_tls = BooleanField('Use TLS')
    mail_username = StringField('SMTP Username')
    mail_password = PasswordField('SMTP Password')
    mail_default_sender = StringField('Default Sender Email', validators=[Optional(), Email()])
    
    submit = SubmitField('Save SMTP Settings')
    test_email = SubmitField('Send Test Email', render_kw={'class': 'btn btn-outline-primary'})

class SystemSettingsForm(FlaskForm):
    # System Settings
    timezone = SelectField('Timezone', choices=[
        ('Asia/Manila', 'Asia/Manila (GMT+8)'),
        ('UTC', 'UTC (GMT+0)'),
        ('America/New_York', 'America/New_York (EST/EDT)'),
        ('Europe/London', 'Europe/London (GMT/BST)'),
        ('Asia/Tokyo', 'Asia/Tokyo (JST)'),
        ('Asia/Shanghai', 'Asia/Shanghai (CST)'),
        ('Asia/Singapore', 'Asia/Singapore (SGT)'),
        ('Australia/Sydney', 'Australia/Sydney (AEST/AEDT)'),
        ('America/Los_Angeles', 'America/Los_Angeles (PST/PDT)'),
        ('America/Chicago', 'America/Chicago (CST/CDT)')
    ])
    
    submit = SubmitField('Save System Settings')

class TestEmailForm(FlaskForm):
    recipient_email = StringField('Test Email Recipient', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Test Email')