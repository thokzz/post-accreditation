from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, TextAreaField, SelectField, IntegerField, 
                    SelectMultipleField, BooleanField, SubmitField, FieldList, FormField)
from wtforms.validators import DataRequired, Email, NumberRange, Length, Optional
from wtforms.widgets import CheckboxInput, ListWidget, TextArea

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SoftwareEntryForm(FlaskForm):
    """Sub-form for software entries"""
    software_name = StringField('Software Name', validators=[DataRequired()])
    version = StringField('Version', validators=[DataRequired()])
    license_count = IntegerField('Number of Licenses', validators=[DataRequired(), NumberRange(min=1)])
    is_free = BooleanField('Free Version (No proof required)')
    proof_file = FileField('Proof of License', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'pdf'], 'Only images and PDF files allowed')
    ])

class WorkstationForm(FlaskForm):
    """Sub-form for workstation details"""
    machine_name = StringField('Machine Name', validators=[DataRequired()])
    functions = MultiCheckboxField('Functions', choices=[
        ('audio_editing', 'Audio Editing'),
        ('video_editing', 'Video Editing'),
        ('graphics', 'Graphics')
    ])
    device_model = StringField('Device Model', validators=[DataRequired()])
    operating_system = StringField('Operating System', validators=[DataRequired()])
    processor = StringField('Processor', validators=[DataRequired()])
    graphics_card = StringField('Graphics Card Model')
    memory = StringField('Memory', validators=[DataRequired()])
    monitor = StringField('Monitor', validators=[DataRequired()])
    monitor_calibrated = SelectField('Monitor Professionally Calibrated?', 
                                   choices=[('yes', 'Yes'), ('no', 'No')])
    io_devices = BooleanField('Has IO Devices (AJA/BlackMagic/Matrox)')
    speaker_model = StringField('Speaker Model')
    headphone_model = StringField('Headphone/Headset Model')

class AccreditationFormSubmission(FlaskForm):
    """Main accreditation form for external submission"""
    
    # Basic Company Information
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=200)])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    contact_number = StringField('Contact Person\'s Number', validators=[DataRequired(), Length(max=20)])
    contact_email = StringField('Contact Person\'s Email', validators=[DataRequired(), Email(), Length(max=120)])
    business_address = TextAreaField('Business Address', validators=[DataRequired()], 
                                   render_kw={'rows': 3})
    business_email = StringField('Business Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    
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
    ], validators=[DataRequired(message='Please select at least one service')])
    
    services_other = StringField('Other Services (please specify)', validators=[Length(max=500)])
    
    # Part 2: Facility Output Technical Specifications
    facility_formats = MultiCheckboxField('Facility Output Technical Specifications', choices=[
        ('4k_uhd_23976', '4K UHD (3849 x 2160), 23.976'),
        ('4k_uhd_2997', '4K UHD (3849 x 2160), 29.97'),
        ('2k_23976', '2K (2048x1080), 23.976'),
        ('2k_2997', '2K (2048x1080), 29.97'),
        ('hd_23976', 'HD (1920x1080), 23.976'),
        ('hd_2997', 'HD (1920x1080), 29.97'),
        ('sd_format', 'SD format')
    ], validators=[DataRequired(message='Please select at least one format')])
    
    # Part 3: Audio Software (conditional - shown if audio services selected)
    audio_software_protools = BooleanField('Protools')
    audio_protools_version = StringField('Version')
    audio_protools_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_protools_free = BooleanField('Free version')
    audio_protools_proof = FileField('Proof of license', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'pdf'], 'Only images and PDF files allowed')
    ])
    
    audio_software_vegas = BooleanField('Vegas')
    audio_vegas_version = StringField('Version')
    audio_vegas_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_vegas_free = BooleanField('Free version')
    audio_vegas_proof = FileField('Proof of license')
    
    audio_software_reason = BooleanField('Reason')
    audio_reason_version = StringField('Version')
    audio_reason_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_reason_free = BooleanField('Free version')
    audio_reason_proof = FileField('Proof of license')
    
    audio_software_reaper = BooleanField('Reaper')
    audio_reaper_version = StringField('Version')
    audio_reaper_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_reaper_free = BooleanField('Free version')
    audio_reaper_proof = FileField('Proof of license')
    
    audio_software_audacity = BooleanField('Audacity')
    audio_audacity_version = StringField('Version')
    audio_audacity_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_audacity_free = BooleanField('Free version')
    audio_audacity_proof = FileField('Proof of license')
    
    audio_software_kontakt = BooleanField('Kontakt')
    audio_kontakt_version = StringField('Version')
    audio_kontakt_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_kontakt_free = BooleanField('Free version')
    audio_kontakt_proof = FileField('Proof of license')
    
    audio_software_other1 = StringField('Other Software 1 (specify)')
    audio_other1_version = StringField('Version')
    audio_other1_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_other1_free = BooleanField('Free version')
    audio_other1_proof = FileField('Proof of license')
    
    audio_software_other2 = StringField('Other Software 2 (specify)')
    audio_other2_version = StringField('Version')
    audio_other2_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    audio_other2_free = BooleanField('Free version')
    audio_other2_proof = FileField('Proof of license')
    
    # Part 4: Editing Software (conditional)
    editing_software_finalcut = BooleanField('Final Cut Pro')
    editing_finalcut_version = StringField('Version')
    editing_finalcut_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    editing_finalcut_free = BooleanField('Free version')
    editing_finalcut_proof = FileField('Proof of license')
    
    editing_software_vegas = BooleanField('Sony Vegas Pro')
    editing_vegas_version = StringField('Version')
    editing_vegas_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    editing_vegas_free = BooleanField('Free version')
    editing_vegas_proof = FileField('Proof of license')
    
    editing_software_avid = BooleanField('Avid Media Composer')
    editing_avid_version = StringField('Version')
    editing_avid_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    editing_avid_free = BooleanField('Free version')
    editing_avid_proof = FileField('Proof of license')
    
    editing_software_premiere = BooleanField('Adobe Premiere Pro')
    editing_premiere_version = StringField('Version (should be 2025.2)')
    editing_premiere_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    editing_premiere_free = BooleanField('Free version')
    editing_premiere_proof = FileField('Proof of license')
    
    editing_software_davinci = BooleanField('DaVinci Resolve')
    editing_davinci_version = StringField('Version')
    editing_davinci_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    editing_davinci_free = BooleanField('Free version')
    editing_davinci_proof = FileField('Proof of license')
    
    editing_software_other1 = StringField('Other Software 1 (specify)')
    editing_other1_version = StringField('Version')
    editing_other1_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    editing_other1_free = BooleanField('Free version')
    editing_other1_proof = FileField('Proof of license')
    
    editing_software_other2 = StringField('Other Software 2 (specify)')
    editing_other2_version = StringField('Version')
    editing_other2_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    editing_other2_free = BooleanField('Free version')
    editing_other2_proof = FileField('Proof of license')
    
    # Part 5: Graphics Software (conditional)
    graphics_software_photoshop = BooleanField('Adobe Photoshop')
    graphics_photoshop_version = StringField('Version')
    graphics_photoshop_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_photoshop_free = BooleanField('Free version')
    graphics_photoshop_proof = FileField('Proof of license')
    
    graphics_software_illustrator = BooleanField('Adobe Illustrator')
    graphics_illustrator_version = StringField('Version')
    graphics_illustrator_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_illustrator_free = BooleanField('Free version')
    graphics_illustrator_proof = FileField('Proof of license')
    
    graphics_software_aftereffects = BooleanField('Adobe After Effects')
    graphics_aftereffects_version = StringField('Version')
    graphics_aftereffects_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_aftereffects_free = BooleanField('Free version')
    graphics_aftereffects_proof = FileField('Proof of license')
    
    graphics_software_coreldraw = BooleanField('Corel Draw')
    graphics_coreldraw_version = StringField('Version')
    graphics_coreldraw_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_coreldraw_free = BooleanField('Free version')
    graphics_coreldraw_proof = FileField('Proof of license')
    
    graphics_software_procreate = BooleanField('ProCreate')
    graphics_procreate_version = StringField('Version')
    graphics_procreate_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_procreate_free = BooleanField('Free version')
    graphics_procreate_proof = FileField('Proof of license')
    
    graphics_software_gimp = BooleanField('Gimp')
    graphics_gimp_version = StringField('Version')
    graphics_gimp_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_gimp_free = BooleanField('Free version')
    graphics_gimp_proof = FileField('Proof of license')
    
    graphics_software_houdini = BooleanField('Houdini')
    graphics_houdini_version = StringField('Version')
    graphics_houdini_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_houdini_free = BooleanField('Free version')
    graphics_houdini_proof = FileField('Proof of license')
    
    graphics_software_inkscape = BooleanField('Inkscape')
    graphics_inkscape_version = StringField('Version')
    graphics_inkscape_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_inkscape_free = BooleanField('Free version')
    graphics_inkscape_proof = FileField('Proof of license')
    
    graphics_software_maya = BooleanField('Autodesk Maya')
    graphics_maya_version = StringField('Version')
    graphics_maya_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_maya_free = BooleanField('Free version')
    graphics_maya_proof = FileField('Proof of license')
    
    graphics_software_3dsmax = BooleanField('Autodesk 3DSMax')
    graphics_3dsmax_version = StringField('Version')
    graphics_3dsmax_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_3dsmax_free = BooleanField('Free version')
    graphics_3dsmax_proof = FileField('Proof of license')
    
    graphics_software_blender = BooleanField('Blender')
    graphics_blender_version = StringField('Version')
    graphics_blender_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_blender_free = BooleanField('Free version')
    graphics_blender_proof = FileField('Proof of license')
    
    graphics_software_cinema4d = BooleanField('Cinema 4D')
    graphics_cinema4d_version = StringField('Version')
    graphics_cinema4d_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_cinema4d_free = BooleanField('Free version')
    graphics_cinema4d_proof = FileField('Proof of license')
    
    graphics_software_other1 = StringField('Other Software 1 (specify)')
    graphics_other1_version = StringField('Version')
    graphics_other1_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_other1_free = BooleanField('Free version')
    graphics_other1_proof = FileField('Proof of license')
    
    graphics_software_other2 = StringField('Other Software 2 (specify)')
    graphics_other2_version = StringField('Version')
    graphics_other2_licenses = IntegerField('No. of licenses', validators=[Optional(), NumberRange(min=1)])
    graphics_other2_free = BooleanField('Free version')
    graphics_other2_proof = FileField('Proof of license')
    
    # Part 6: Staff Information (conditional based on Part 1)
    has_audio_engineers = BooleanField('Do you have in-house Audio Engineers/Editors?')
    audio_engineers_count = IntegerField('How many?', validators=[Optional(), NumberRange(min=0)])
    
    has_video_editors = BooleanField('Do you have in-house Video Editors?')
    video_editors_count = IntegerField('How many?', validators=[Optional(), NumberRange(min=0)])
    
    has_colorists = BooleanField('Do you have in-house Colorists?')
    colorists_count = IntegerField('How many?', validators=[Optional(), NumberRange(min=0)])
    
    has_graphics_artists = BooleanField('Do you have in-house Graphics Artists?')
    graphics_artists_count = IntegerField('How many?', validators=[Optional(), NumberRange(min=0)])
    
    has_animators = BooleanField('Do you have in-house Animators?')
    animators_count = IntegerField('How many?', validators=[Optional(), NumberRange(min=0)])
    
    # Part 7: Hardware Specifications
    total_workstations = IntegerField('Total Number of workstations in the facility', 
                                    validators=[DataRequired(), NumberRange(min=1)])
    workstations_shared = SelectField('Are these hardware workstations shared across different services?', 
                                    choices=[
                                        ('yes', 'Yes'),
                                        ('no', 'No'),
                                        ('mixed', 'Mixed')
                                    ], validators=[DataRequired()])
    
    floor_plan = FileField('Floor plan (top view) of work areas', validators=[
        FileRequired(),
        FileAllowed(['png', 'jpg', 'jpeg', 'pdf'], 'Only images and PDF files allowed')
    ])
    
    # Dynamic workstation fields would be generated based on total_workstations
    # For now, we'll include a few static ones as an example
    workstation1_machine_name = StringField('Machine Name (Workstation 1)')
    workstation1_functions = MultiCheckboxField('Functions', choices=[
        ('audio_editing', 'Audio Editing'),
        ('video_editing', 'Video Editing'),
        ('graphics', 'Graphics')
    ])
    workstation1_device_model = StringField('Device Model')
    workstation1_operating_system = StringField('Operating System')
    workstation1_processor = StringField('Processor')
    workstation1_graphics_card = StringField('Graphics Card Model')
    workstation1_memory = StringField('Memory')
    workstation1_monitor = StringField('Monitor')
    workstation1_monitor_calibrated = SelectField('Monitor Professionally Calibrated?', 
                                                choices=[('yes', 'Yes'), ('no', 'No')])
    workstation1_io_devices = BooleanField('Has IO Devices (AJA/BlackMagic/Matrox)')
    workstation1_speaker_model = StringField('Speaker Model')
    workstation1_headphone_model = StringField('Headphone/Headset Model')
    
    # Part 8: Certification
    accomplished_by = StringField('Accomplished by (Name)', validators=[DataRequired(), Length(max=100)])
    signature_file = FileField('Upload Signature', validators=[
        FileRequired(),
        FileAllowed(['png', 'jpg', 'jpeg'], 'Only image files allowed for signature')
    ])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=100)])
    
    submit = SubmitField('Submit Accreditation Form')


class ApprovalForm(FlaskForm):
    """Form for approving/rejecting accreditation forms"""
    action = SelectField('Action', choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('needs_revision', 'Request Revision')
    ], validators=[DataRequired()])
    
    comments = TextAreaField('Comments for Applicant', 
                           render_kw={'rows': 4, 'placeholder': 'Comments visible to the applicant...'})
    
    internal_notes = TextAreaField('Internal Notes', 
                                 render_kw={'rows': 3, 'placeholder': 'Internal notes (not visible to applicant)...'})
    
    submit = SubmitField('Submit Review')


class FormSearchForm(FlaskForm):
    """Form for searching accreditation forms"""
    search = StringField('Search', render_kw={'placeholder': 'Search by company name, contact person, or email...'})
    status = SelectField('Status', choices=[
        ('all', 'All Status'),
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])
    submit = SubmitField('Search')
