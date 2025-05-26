from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from wtforms.widgets import TextArea
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class TwoFactorForm(FlaskForm):
    token = StringField('Verification Code', validators=[
        DataRequired(), 
        Length(min=6, max=6, message='Verification code must be 6 digits')
    ], render_kw={'placeholder': '000000', 'autocomplete': 'off'})
    submit = SubmitField('Verify')

class Setup2FAForm(FlaskForm):
    token = StringField('Verification Code', validators=[
        DataRequired(), 
        Length(min=6, max=6, message='Verification code must be 6 digits')
    ], render_kw={'placeholder': '000000', 'autocomplete': 'off'})
    submit = SubmitField('Enable 2FA')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=1, max=80, message='First name must be between 1 and 80 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(min=1, max=80, message='Last name must be between 1 and 80 characters')
    ])
    role = SelectField('Role', choices=[
        ('viewer', 'Viewer/User'),
        ('approver', 'Approver'),
        ('manager', 'Manager'),
        ('administrator', 'Administrator')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        """Validate username uniqueness"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Validate email uniqueness"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=1, max=80, message='First name must be between 1 and 80 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(min=1, max=80, message='Last name must be between 1 and 80 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """Validate email uniqueness (excluding current user)"""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please choose a different one.')
