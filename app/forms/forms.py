# app/forms/forms.py - Complete Form Classes for Forms Blueprint
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (StringField, TextAreaField, SelectField, IntegerField, 
                     SelectMultipleField, FieldList, FormField, BooleanField, 
                     SubmitField, HiddenField)
from wtforms.validators import DataRequired, Email, NumberRange, Optional, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class FormAccessForm(FlaskForm):
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Access Form')

class SoftwareDetailsForm(FlaskForm):
    """Subform for software details"""
    name = StringField('Software Name')
    custom_name = StringField('Custom Name')  # For "Others"
    version = StringField('Version')
    licenses = IntegerField('Number of Licenses', validators=[Optional(), NumberRange(min=0)])
    is_free = BooleanField('Free Version')
    proof_file = FileField('Proof of License', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!')
    ])

class WorkstationDetailsForm(FlaskForm):
    """Subform for workstation details"""
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
    io_devices = StringField('IO Devices (Aja/BlackMagic/Matrox)')
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
    
    # Part 1: Services Offered
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
    
    # Part 2: Technical Specifications
    facility_formats = MultiCheckboxField('Facility Output Technical Specifications', choices=[
        ('4k_23976', '4K UHD (3849 x 2160), 23.976'),
        ('4k_2997', '4K UHD (3849 x 2160), 29.97'),
        ('2k_23976', '2K (2048x1080), 23.976'),
        ('2k_2997', '2K (2048x1080), 29.97'),
        ('hd_23976', 'HD (1920x1080), 23.976'),
        ('hd_2997', 'HD (1920x1080), 29.97'),
        ('sd', 'SD format')
    ])
    
    # Part 3: Audio Software (Dynamic - will be handled via JavaScript)
    # These fields will capture the submitted data
    audio_software_names = FieldList(StringField('Software Name'), min_entries=0)
    audio_software_versions = FieldList(StringField('Version'), min_entries=0)
    audio_software_licenses = FieldList(IntegerField('Licenses'), min_entries=0)
    audio_software_free = FieldList(BooleanField('Free'), min_entries=0)
    
    # Part 4: Editing Software (Dynamic)
    editing_software_names = FieldList(StringField('Software Name'), min_entries=0)
    editing_software_versions = FieldList(StringField('Version'), min_entries=0)
    editing_software_licenses = FieldList(IntegerField('Licenses'), min_entries=0)
    editing_software_free = FieldList(BooleanField('Free'), min_entries=0)
    
    # Part 5: Graphics Software (Dynamic)
    graphics_software_names = FieldList(StringField('Software Name'), min_entries=0)
    graphics_software_versions = FieldList(StringField('Version'), min_entries=0)
    graphics_software_licenses = FieldList(IntegerField('Licenses'), min_entries=0)
    graphics_software_free = FieldList(BooleanField('Free'), min_entries=0)
    
    # Part 6: Staff Information
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
    
    # Part 7: Hardware Information
    total_workstations = IntegerField('Total Number of Workstations', 
                                    validators=[DataRequired(), NumberRange(min=1)])
    workstations_shared = SelectField('Are workstations shared across services?', 
                                    choices=[('Y', 'Yes'), ('N', 'No'), ('Mixed', 'Mixed')],
                                    validators=[DataRequired()])
    floor_plan = FileField('Floor Plan Upload', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!')
    ])
    
    # Workstation Details (Dynamic - handled via JavaScript)
    workstation_details = FieldList(FormField(WorkstationDetailsForm), min_entries=0)
    
    # Part 8: Certification
    accomplished_by = StringField('Accomplished by', validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired()])
    signature_file = FileField('Upload Signature', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!'),
        DataRequired()
    ])
    
    submit = SubmitField('Submit Form')
    
    def validate_services_offered(self, field):
        """Ensure at least one service is selected"""
        if not field.data and not self.others_service.data:
            raise ValidationError('Please select at least one service or specify in "Others".')
    
    def validate_editing_software_versions(self, field):
        """Validate Adobe Premiere Pro version if selected"""
        if self.editing_software_names.data:
            for i, name in enumerate(self.editing_software_names.data):
                if name == 'premiere' and self.editing_software_versions.data[i]:
                    version = self.editing_software_versions.data[i]
                    # Simple check for version 2025.2 or higher
                    try:
                        major, minor = version.split('.')[:2]
                        if int(major) < 2025 or (int(major) == 2025 and int(minor) < 2):
                            raise ValidationError('Adobe Premiere Pro must be version 2025.2 or higher.')
                    except:
                        pass  # If version format is different, skip validation