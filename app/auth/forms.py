# app/auth/forms.py - Authentication Forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class TwoFactorForm(FlaskForm):
    token = StringField('Authentication Code', validators=[
        DataRequired(), 
        Length(min=6, max=6, message='Authentication code must be 6 digits')
    ])
    submit = SubmitField('Verify')
