# app/forms/forms.py - Form Classes for Forms Blueprint
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, TextAreaField, SelectField, IntegerField, 
                     SelectMultipleField, FieldList, FormField, BooleanField, 
                     SubmitField, HiddenField)
from wtforms.validators import DataRequired, Email, NumberRange, Optional
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class FormAccessForm(FlaskForm):
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Access Form')

class SoftwareDetailsForm(FlaskForm):
    name = StringField('Software Name')
    version = StringField('Version')
    licenses = IntegerField('Number of Licenses')
    is_free = BooleanField('Free Version')
    proof_file = FileField('Proof of License')

class WorkstationForm(FlaskForm):
    machine_name = StringField('Machine Name')
    functions = MultiCheckboxField('Functions', choices=[
        ('audio', 'Audio Editing'),
        ('video', 'Video Editing'),
        ('graphics', 'Graphics')
    ])
    device_model = StringField('Device Model')
    operating_system = StringField('Operating System')
    processor = StringField('Processor')
    graphics_card = StringField('Graphics Card Model')
    memory = StringField('Memory')
    monitor = StringField('Monitor')
    monitor_calibrated = SelectField('Monitor Professionally Calibrated?', 
                                   choices=[('yes', 'Yes'), ('no', 'No')])
    io_devices = BooleanField('IO Devices (Aja/BlackMagic/Matrox)')
    speaker_model = StringField('Speaker Model')
    headphone_model = StringField('Headphone/Headset Model')

class AccreditationForm(FlaskForm):
    # Company Information
    company_name = StringField('Company Name', validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])
    business_address = TextAreaField('Business Address', validators=[DataRequired()])
    business_email = StringField('Business Email', validators=[DataRequired(), Email()])
    
    # Services Offered
    services_offered = MultiCheckboxField('Services Offered', choices=[
        ('adr', 'Automatic Dialogue Replacement (dubbing)'),
        ('musical_scoring', 'Musical Scoring'),
        ('sound_design', 'Sound Design'),
        ('audio_editing', 'Audio Editing/Mixing'),
        ('music_research', 'Music Research'),
        ('music_clearance', 'Music Use Clearance'),
        ('music_creation', 'Music Creation'),
        ('video_editing', 'Video Editing'),
        ('color_correction', 'Color Correction and Color Grading'),
        ('compositing', 'Compositing'),
        ('2d_animation', '2D Animation'),
        ('3d_animation', '3D Animation'),
        ('special_effects', 'Special Effects')
    ])
    others_service = StringField('Others (please specify)')
    
    # Technical Specifications
    facility_formats = MultiCheckboxField('Facility Output Technical Specifications', choices=[
        ('4k_23976', '4K UHD (3849 x 2160), 23.976'),
        ('4k_2997', '4K UHD (3849 x 2160), 29.97'),
        ('2k_23976', '2K (2048x1080), 23.976'),
        ('2k_2997', '2K (2048x1080), 29.97'),
        ('hd_23976', 'HD (1920x1080), 23.976'),
        ('hd_2997', 'HD (1920x1080), 29.97'),
        ('sd', 'SD format')
    ])
    
    # Staff Information
    audio_engineers_count = IntegerField('Number of Audio Engineers/Editors', 
                                       validators=[Optional(), NumberRange(min=0)])
    video_editors_count = IntegerField('Number of Video Editors', 
                                     validators=[Optional(), NumberRange(min=0)])
    colorists_count = IntegerField('Number of Colorists', 
                                 validators=[Optional(), NumberRange(min=0)])
    graphics_artists_count = IntegerField('Number of Graphics Artists', 
                                        validators=[Optional(), NumberRange(min=0)])
    animators_count = IntegerField('Number of Animators', 
                                 validators=[Optional(), NumberRange(min=0)])
    
    # Hardware Information
    total_workstations = IntegerField('Total Number of Workstations', 
                                    validators=[DataRequired(), NumberRange(min=1)])
    workstations_shared = SelectField('Are workstations shared across services?', 
                                    choices=[('Y', 'Yes'), ('N', 'No'), ('Mixed', 'Mixed')])
    floor_plan = FileField('Floor Plan Upload', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!')
    ])
    
    # Certification
    accomplished_by = StringField('Accomplished by', validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired()])
    signature_file = FileField('Upload Signature', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!')
    ])
    
    submit = SubmitField('Submit Form')
