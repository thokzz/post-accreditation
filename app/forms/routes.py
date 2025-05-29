# app/forms/routes.py - Complete form handling with all parts
from flask import render_template, redirect, url_for, flash, request, abort, session
from app.forms import bp
from app.models import FormLink, FormSubmission, FormAttachment
from app.forms.forms import AccreditationForm, FormAccessForm
from app.utils import save_file, hash_password, log_audit_event
from app import db
import hashlib
from datetime import datetime, timezone
import json

@bp.route('/access/<token>', methods=['GET', 'POST'])
def form_access(token):
    form_link = FormLink.query.filter_by(unique_token=token, is_active=True).first()
    if not form_link:
        abort(404)
    
    access_form = FormAccessForm()
    if access_form.validate_on_submit():
        password_hash = hash_password(access_form.password.data)
        if password_hash == form_link.password:
            session['form_access_token'] = token
            return redirect(url_for('forms.accreditation_form', token=token))
        else:
            flash('Invalid password', 'error')
    
    return render_template('forms/access.html', form=access_form, token=token)

@bp.route('/form/<token>', methods=['GET', 'POST'])
def accreditation_form(token):
    if session.get('form_access_token') != token:
        return redirect(url_for('forms.form_access', token=token))
    
    form_link = FormLink.query.filter_by(unique_token=token, is_active=True).first()
    if not form_link:
        abort(404)
    
    form = AccreditationForm()
    
    if form.validate_on_submit():
        # Process software data from request
        audio_software = process_software_data(request, 'audio')
        editing_software = process_software_data(request, 'editing')
        graphics_software = process_software_data(request, 'graphics')
        
        # Process workstation data
        workstation_details = process_workstation_data(request)
        
        # Create submission
        submission = FormSubmission(
            form_link_id=form_link.id,
            company_name=form.company_name.data,
            contact_person=form.contact_person.data,
            contact_number=form.contact_number.data,
            contact_email=form.contact_email.data,
            business_address=form.business_address.data,
            business_email=form.business_email.data,
            services_offered=form.services_offered.data,
            others_service=form.others_service.data,
            facility_formats=form.facility_formats.data,
            audio_software=audio_software,
            editing_software=editing_software,
            graphics_software=graphics_software,
            audio_engineers_count=form.audio_engineers_count.data,
            video_editors_count=form.video_editors_count.data,
            colorists_count=form.colorists_count.data,
            graphics_artists_count=form.graphics_artists_count.data,
            animators_count=form.animators_count.data,
            total_workstations=form.total_workstations.data,
            workstations_shared=form.workstations_shared.data,
            workstation_details=workstation_details,
            accomplished_by=form.accomplished_by.data,
            designation=form.designation.data
        )
        
        db.session.add(submission)
        db.session.flush()  # Get the ID
        
        # Handle file uploads
        # Signature file
        if form.signature_file.data:
            filename, file_path = save_file(form.signature_file.data, 'signatures')
            if filename:
                submission.signature_file = filename
                attachment = FormAttachment(
                    submission_id=submission.id,
                    filename=filename,
                    original_filename=form.signature_file.data.filename,
                    file_path=file_path,
                    attachment_type='signature',
                    file_size=len(form.signature_file.data.read())
                )
                form.signature_file.data.seek(0)  # Reset file pointer
                db.session.add(attachment)
        
        # Floor plan upload
        if form.floor_plan.data:
            filename, file_path = save_file(form.floor_plan.data, 'floor_plans')
            if filename:
                attachment = FormAttachment(
                    submission_id=submission.id,
                    filename=filename,
                    original_filename=form.floor_plan.data.filename,
                    file_path=file_path,
                    attachment_type='floor_plan',
                    file_size=len(form.floor_plan.data.read())
                )
                form.floor_plan.data.seek(0)
                db.session.add(attachment)
        
        # Software proof uploads
        handle_software_proofs(request, submission.id, 'audio')
        handle_software_proofs(request, submission.id, 'editing')
        handle_software_proofs(request, submission.id, 'graphics')
        
        db.session.commit()
        
        # Mark form link as used
        form_link.used_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Clear session
        session.pop('form_access_token', None)
        
        flash('Form submitted successfully!', 'success')
        return redirect(url_for('forms.submission_success'))
    
    return render_template('forms/accreditation.html', form=form, token=token)

@bp.route('/success')
def submission_success():
    return render_template('forms/success.html')

def process_software_data(request, software_type):
    """Process dynamic software entries from form"""
    software_list = []
    
    names = request.form.getlist(f'{software_type}_software_name[]')
    versions = request.form.getlist(f'{software_type}_software_version[]')
    licenses = request.form.getlist(f'{software_type}_software_licenses[]')
    free_versions = request.form.getlist(f'{software_type}_software_free[]')
    
    for i in range(len(names)):
        if names[i]:  # Only process if name is provided
            software_entry = {
                'name': names[i],
                'version': versions[i] if i < len(versions) else '',
                'licenses': int(licenses[i]) if i < len(licenses) and licenses[i] else 0,
                'is_free': f'{software_type}_software_free_{i}' in request.form
            }
            
            # Handle custom name for "other" option
            if names[i] == 'other':
                custom_names = request.form.getlist(f'{software_type}_software_custom_name[]')
                if i < len(custom_names):
                    software_entry['custom_name'] = custom_names[i]
            
            software_list.append(software_entry)
    
    return software_list

def process_workstation_data(request):
    """Process dynamic workstation entries from form"""
    workstation_list = []
    
    machine_names = request.form.getlist('workstation_machine_name[]')
    device_models = request.form.getlist('workstation_device_model[]')
    operating_systems = request.form.getlist('workstation_os[]')
    processors = request.form.getlist('workstation_processor[]')
    graphics_cards = request.form.getlist('workstation_graphics[]')
    memories = request.form.getlist('workstation_memory[]')
    monitors = request.form.getlist('workstation_monitor[]')
    monitor_calibrated = request.form.getlist('workstation_monitor_calibrated[]')
    io_devices = request.form.getlist('workstation_io_devices[]')
    speakers = request.form.getlist('workstation_speakers[]')
    headphones = request.form.getlist('workstation_headphones[]')
    
    for i in range(len(machine_names)):
        if machine_names[i]:  # Only process if machine name is provided
            workstation_entry = {
                'machine_name': machine_names[i],
                'functions': {
                    'audio': f'workstation_functions_audio[{i}]' in request.form,
                    'video': f'workstation_functions_video[{i}]' in request.form,
                    'graphics': f'workstation_functions_graphics[{i}]' in request.form
                },
                'device_model': device_models[i] if i < len(device_models) else '',
                'operating_system': operating_systems[i] if i < len(operating_systems) else '',
                'processor': processors[i] if i < len(processors) else '',
                'graphics_card': graphics_cards[i] if i < len(graphics_cards) else '',
                'memory': memories[i] if i < len(memories) else '',
                'monitor': monitors[i] if i < len(monitors) else '',
                'monitor_calibrated': monitor_calibrated[i] if i < len(monitor_calibrated) else 'no',
                'io_devices': io_devices[i] if i < len(io_devices) else '',
                'speakers': speakers[i] if i < len(speakers) else '',
                'headphones': headphones[i] if i < len(headphones) else ''
            }
            workstation_list.append(workstation_entry)
    
    return workstation_list

def handle_software_proofs(request, submission_id, software_type):
    """Handle software proof file uploads"""
    proof_files = request.files.getlist(f'{software_type}_software_proof[]')
    
    for i, file in enumerate(proof_files):
        if file and file.filename:
            filename, file_path = save_file(file, f'software_proofs/{software_type}')
            if filename:
                attachment = FormAttachment(
                    submission_id=submission_id,
                    filename=filename,
                    original_filename=file.filename,
                    file_path=file_path,
                    attachment_type=f'{software_type}_software_proof_{i}',
                    file_size=len(file.read())
                )
                file.seek(0)
                db.session.add(attachment)