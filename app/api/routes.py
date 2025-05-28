# app/api/routes.py
from flask import jsonify, send_file, abort
from flask_login import login_required, current_user
from app.api import bp
from app.models import FormSubmission, UserRole
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

@bp.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    try:
        # Simple database check
        from app.models import User
        user_count = User.query.count()
        return jsonify({
            'status': 'healthy',
            'service': 'post-accreditation',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'users': user_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'post-accreditation',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@bp.route('/submission/<int:id>/pdf')
@login_required
def generate_pdf(id):
    """Generate PDF report for approved submission"""
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.MANAGER]:
        abort(403)
    
    submission = FormSubmission.query.get_or_404(id)
    
    if submission.status != 'approved':
        abort(400, description="Only approved submissions can generate PDF")
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("GMA Network Post Production Accreditation Certificate", title_style))
    story.append(Spacer(1, 20))
    
    # Company Info
    story.append(Paragraph("Company Information", styles['Heading2']))
    company_data = [
        ['Company Name:', submission.company_name],
        ['Contact Person:', submission.contact_person],
        ['Contact Number:', submission.contact_number],
        ['Contact Email:', submission.contact_email],
        ['Business Email:', submission.business_email],
        ['Business Address:', submission.business_address],
    ]
    
    company_table = Table(company_data, colWidths=[2*inch, 4*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(company_table)
    story.append(Spacer(1, 20))
    
    # Services Offered
    if submission.services_offered:
        story.append(Paragraph("Services Offered", styles['Heading2']))
        service_mapping = {
            'adr': 'Automatic Dialogue Replacement (dubbing)',
            'musical_scoring': 'Musical Scoring',
            'sound_design': 'Sound Design',
            'audio_editing': 'Audio Editing/Mixing',
            'music_research': 'Music Research',
            'music_clearance': 'Music Use Clearance',
            'music_creation': 'Music Creation',
            'video_editing': 'Video Editing',
            'color_correction': 'Color Correction and Color Grading',
            'compositing': 'Compositing',
            '2d_animation': '2D Animation',
            '3d_animation': '3D Animation',
            'special_effects': 'Special Effects'
        }
        
        services_list = []
        for service in submission.services_offered:
            services_list.append(service_mapping.get(service, service))
        
        for service in services_list:
            story.append(Paragraph(f"• {service}", styles['Normal']))
        
        if submission.others_service:
            story.append(Paragraph(f"• {submission.others_service}", styles['Normal']))
        
        story.append(Spacer(1, 20))
    
    # Technical Specifications
    if submission.facility_formats:
        story.append(Paragraph("Technical Specifications", styles['Heading2']))
        format_mapping = {
            '4k_23976': '4K UHD (3849 x 2160), 23.976',
            '4k_2997': '4K UHD (3849 x 2160), 29.97',
            '2k_23976': '2K (2048x1080), 23.976',
            '2k_2997': '2K (2048x1080), 29.97',
            'hd_23976': 'HD (1920x1080), 23.976',
            'hd_2997': 'HD (1920x1080), 29.97',
            'sd': 'SD format'
        }
        
        for format_key in submission.facility_formats:
            format_name = format_mapping.get(format_key, format_key)
            story.append(Paragraph(f"• {format_name}", styles['Normal']))
        
        story.append(Spacer(1, 20))
    
    # Staff Information
    story.append(Paragraph("Staff Information", styles['Heading2']))
    staff_data = []
    if submission.audio_engineers_count:
        staff_data.append(['Audio Engineers/Editors:', str(submission.audio_engineers_count)])
    if submission.video_editors_count:
        staff_data.append(['Video Editors:', str(submission.video_editors_count)])
    if submission.colorists_count:
        staff_data.append(['Colorists:', str(submission.colorists_count)])
    if submission.graphics_artists_count:
        staff_data.append(['Graphics Artists:', str(submission.graphics_artists_count)])
    if submission.animators_count:
        staff_data.append(['Animators:', str(submission.animators_count)])
    
    if staff_data:
        staff_table = Table(staff_data, colWidths=[2*inch, 1*inch])
        staff_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(staff_table)
    
    story.append(Spacer(1, 20))
    
    # Hardware Information
    story.append(Paragraph("Hardware Information", styles['Heading2']))
    hardware_data = [
        ['Total Workstations:', str(submission.total_workstations)],
        ['Workstations Shared:', submission.workstations_shared],
    ]
    
    hardware_table = Table(hardware_data, colWidths=[2*inch, 2*inch])
    hardware_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(hardware_table)
    story.append(Spacer(1, 30))
    
    # Certification
    story.append(Paragraph("Certification", styles['Heading2']))
    cert_data = [
        ['Accomplished by:', submission.accomplished_by],
        ['Designation:', submission.designation],
        ['Date Approved:', submission.submitted_at.strftime('%Y-%m-%d')],
    ]
    
    cert_table = Table(cert_data, colWidths=[2*inch, 3*inch])
    cert_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(cert_table)
    story.append(Spacer(1, 40))
    
    # Approval Statement
    approval_style = ParagraphStyle(
        'ApprovalStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("This certificate confirms that the above company has been accredited for post-production services with GMA Network.", approval_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    filename = f"accreditation_certificate_{submission.company_name.replace(' ', '_')}_{submission.id}.pdf"
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )