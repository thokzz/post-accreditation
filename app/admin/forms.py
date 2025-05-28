# app/admin/forms.py - Admin Forms
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

class SettingsForm(FlaskForm):
    # SMTP Settings
    mail_server = StringField('SMTP Server')
    mail_port = IntegerField('SMTP Port', validators=[Optional(), NumberRange(min=1, max=65535)])
    mail_use_tls = BooleanField('Use TLS')
    mail_username = StringField('SMTP Username')
    mail_password = PasswordField('SMTP Password')
    
    # System Settings
    timezone = SelectField('Timezone', choices=[
        ('Asia/Manila', 'Asia/Manila'),
        ('UTC', 'UTC'),
        ('America/New_York', 'America/New_York'),
        ('Europe/London', 'Europe/London')
    ])
    
    submit = SubmitField('Save Settings')
