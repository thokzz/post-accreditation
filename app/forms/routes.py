# app/forms/routes.py - Fixed imports
from flask import render_template, redirect, url_for, flash, request, abort, session
from app.forms import bp
from app.models import FormLink, FormSubmission, FormAttachment
from app.forms.forms import AccreditationForm, FormAccessForm
from app.utils import save_file, hash_password, log_audit_event
from app import db
import hashlib
from datetime import datetime, timezone

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
            audio_engineers_count=form.audio_engineers_count.data,
            video_editors_count=form.video_editors_count.data,
            colorists_count=form.colorists_count.data,
            graphics_artists_count=form.graphics_artists_count.data,
            animators_count=form.animators_count.data,
            total_workstations=form.total_workstations.data,
            workstations_shared=form.workstations_shared.data,
            accomplished_by=form.accomplished_by.data,
            designation=form.designation.data
        )
        
        db.session.add(submission)
        db.session.flush()  # Get the ID
        
        # Handle file uploads
        if form.signature_file.data:
            filename, file_path = save_file(form.signature_file.data, 'signatures')
            if filename:
                submission.signature_file = filename
                attachment = FormAttachment(
                    submission_id=submission.id,
                    filename=filename,
                    original_filename=form.signature_file.data.filename,
                    file_path=file_path,
                    attachment_type='signature'
                )
                db.session.add(attachment)
        
        # Handle floor plan upload
        if form.floor_plan.data:
            filename, file_path = save_file(form.floor_plan.data, 'floor_plans')
            if filename:
                attachment = FormAttachment(
                    submission_id=submission.id,
                    filename=filename,
                    original_filename=form.floor_plan.data.filename,
                    file_path=file_path,
                    attachment_type='floor_plan'
                )
                db.session.add(attachment)
        
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
