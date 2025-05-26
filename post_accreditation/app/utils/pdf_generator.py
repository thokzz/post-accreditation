from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import io

def generate_accreditation_pdf(form, output_path=None):
    """Generate PDF report for accreditation form"""
    
    # Create buffer if no output path specified
    if output_path is None:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
    else:
        doc = SimpleDocTemplate(output_path, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=15,
        textColor=colors.darkgreen
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Build story (content)
    story = []
    
    # Title
    story.append(Paragraph("GMA POST ACCREDITATION FORM", title_style))
    story.append(Spacer(1, 20))
    
    # Form guidelines
    story.append(Paragraph("Form Guidelines:", heading_style))
    guidelines = [
        "1. Review the entire checklist",
        "2. Check only the appropriate items and indicate all needed information",
        "3. Answer the document truthfully"
    ]
    for guideline in guidelines:
        story.append(Paragraph(guideline, normal_style))
    story.append(Spacer(1, 15))
    
    # Form note
    story.append(Paragraph("Form Note:", heading_style))
    note_text = """Third-party supplier' hardware (cameras, external storage, editing facilities, etc.) must adhere with GMA Post Production's facility requirements. The materials or output generated from your facility must conform to GMA's standard. Coordinate with GMA program team regarding these requirements. When a project is conformed or exported from your editing facility, these should already be compliant to the requirements of the Program/Show who availed your service."""
    story.append(Paragraph(note_text, normal_style))
    story.append(Spacer(1, 20))
    
    # Company Information
    story.append(Paragraph("COMPANY INFORMATION", heading_style))
    
    company_data = [
        ['Company Name:', form.company_name],
        ['Contact Person:', form.contact_person],
        ['Contact Number:', form.contact_number],
        ['Contact Email:', form.contact_email],
        ['Business Address:', form.business_address],
        ['Business Email:', form.business_email],
    ]
    
    company_table = Table(company_data, colWidths=[2*inch, 4*inch])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(company_table)
    story.append(Spacer(1, 20))
    
    # Part 1: Services Offered
    story.append(Paragraph("PART 1: SERVICES OFFERED", heading_style))
    services_offered = form.get_services_offered()
    
    services_map = {
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
    
    for service_key, service_name in services_map.items():
        checked = "☑" if service_key in services_offered else "☐"
        story.append(Paragraph(f"{checked} {service_name}", normal_style))
    
    if form.services_other:
        story.append(Paragraph(f"☑ Others: {form.services_other}", normal_style))
    
    story.append(Spacer(1, 15))
    
    # Part 2: Facility Output Technical Specifications
    story.append(Paragraph("PART 2: FACILITY OUTPUT TECHNICAL SPECIFICATIONS", heading_style))
    facility_formats = form.get_facility_formats()
    
    formats_map = {
        '4k_uhd_23976': '4K UHD (3849 x 2160), 23.976',
        '4k_uhd_2997': '4K UHD (3849 x 2160), 29.97',
        '2k_23976': '2K (2048x1080), 23.976',
        '2k_2997': '2K (2048x1080), 29.97',
        'hd_23976': 'HD (1920x1080), 23.976',
        'hd_2997': 'HD (1920x1080), 29.97',
        'sd_format': 'SD format'
    }
    
    for format_key, format_name in formats_map.items():
        checked = "☑" if format_key in facility_formats else "☐"
        story.append(Paragraph(f"{checked} {format_name}", normal_style))
    
    story.append(Spacer(1, 15))
    
    # Software sections (Parts 3, 4, 5)
    software_sections = [
        ('PART 3: AUDIO SOFTWARE OFFERINGS', 'audio'),
        ('PART 4: EDITING SOFTWARE OFFERINGS', 'editing'),
        ('PART 5: GRAPHICS SOFTWARE OFFERINGS', 'graphics')
    ]
    
    for section_title, software_type in software_sections:
        story.append(Paragraph(section_title, heading_style))
        software_data = form.get_software_data(software_type)
        
        if software_data:
            # Create table for software
            table_data = [['Software Name', 'Version', 'No. of Licenses', 'Proof of License']]
            
            for software in software_data:
                proof_status = "Free Version" if software.get('is_free') else "License Required"
                table_data.append([
                    software.get('name', ''),
                    software.get('version', ''),
                    str(software.get('licenses', '')),
                    proof_status
                ])
            
            software_table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch])
            software_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(software_table)
        else:
            story.append(Paragraph("No software specified for this category.", normal_style))
        
        story.append(Spacer(1, 15))
    
    # Part 6: Staff Information
    story.append(Paragraph("PART 6: STAFF INFORMATION", heading_style))
    
    staff_data = [
        ['Audio Engineers/Editors:', f"{form.audio_engineers_count or 0}"],
        ['Video Editors:', f"{form.video_editors_count or 0}"],
        ['Colorists:', f"{form.colorists_count or 0}"],
        ['Graphics Artists:', f"{form.graphics_artists_count or 0}"],
        ['Animators:', f"{form.animators_count or 0}"],
    ]
    
    staff_table = Table(staff_data, colWidths=[3*inch, 2*inch])
    staff_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(staff_table)
    story.append(Spacer(1, 15))
    
    # Part 7: Hardware Specifications
    story.append(Paragraph("PART 7: HARDWARE SPECIFICATIONS", heading_style))
    
    hardware_data = [
        ['Total Number of Workstations:', str(form.total_workstations)],
        ['Workstations Shared:', form.workstations_shared.title() if form.workstations_shared else 'Not specified'],
    ]
    
    hardware_table = Table(hardware_data, colWidths=[3*inch, 2*inch])
    hardware_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(hardware_table)
    story.append(Spacer(1, 15))
    
    # Workstation Details
    workstation_details = form.get_workstation_details()
    if workstation_details:
        story.append(Paragraph("Workstation Details:", subheading_style))
        for i, workstation in enumerate(workstation_details, 1):
            story.append(Paragraph(f"Workstation {i}:", subheading_style))
            
            ws_data = [
                ['Machine Name:', workstation.get('machine_name', '')],
                ['Functions:', ', '.join(workstation.get('functions', []))],
                ['Device Model:', workstation.get('device_model', '')],
                ['Operating System:', workstation.get('operating_system', '')],
                ['Processor:', workstation.get('processor', '')],
                ['Graphics Card:', workstation.get('graphics_card', '')],
                ['Memory:', workstation.get('memory', '')],
                ['Monitor:', workstation.get('monitor', '')],
                ['Monitor Calibrated:', workstation.get('monitor_calibrated', '')],
                ['IO Devices:', 'Yes' if workstation.get('io_devices') else 'No'],
                ['Speaker Model:', workstation.get('speaker_model', '')],
                ['Headphone Model:', workstation.get('headphone_model', '')],
            ]
            
            ws_table = Table(ws_data, colWidths=[2*inch, 3.5*inch])
            ws_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(ws_table)
            story.append(Spacer(1, 10))
    
    # Part 8: Certification
    story.append(PageBreak())
    story.append(Paragraph("PART 8: CERTIFICATION", heading_style))
    
    cert_text = "This is to certify that all information stated above are true and that all software/hardware declarations are covered with genuine Operating Systems as well as licenses."
    story.append(Paragraph(cert_text, normal_style))
    story.append(Spacer(1, 20))
    
    cert_data = [
        ['Accomplished by:', form.accomplished_by],
        ['Designation:', form.designation],
        ['Date Submitted:', form.submitted_at.strftime('%B %d, %Y') if form.submitted_at else 'Not submitted'],
    ]
    
    cert_table = Table(cert_data, colWidths=[2*inch, 3*inch])
    cert_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cert_table)
    story.append(Spacer(1, 20))
    
    # Approval Status
    if form.status != 'draft':
        story.append(Paragraph("APPROVAL STATUS", heading_style))
        
        current_approval = form.get_current_approval()
        if current_approval:
            approval_data = [
                ['Status:', form.status.replace('_', ' ').title()],
                ['Reviewed by:', current_approval.approver.full_name if current_approval.approver else 'N/A'],
                ['Review Date:', current_approval.reviewed_at.strftime('%B %d, %Y') if current_approval.reviewed_at else 'Pending'],
                ['Comments:', current_approval.comments or 'No comments']
            ]
            
            approval_table = Table(approval_data, colWidths=[2*inch, 3.5*inch])
            approval_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(approval_table)
    
    # Footer
    story.append(Spacer(1, 40))
    footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    if output_path is None:
        buffer.seek(0)
        return buffer
    else:
        return output_path

def generate_form_summary_pdf(forms, output_path=None):
    """Generate summary PDF of multiple forms"""
    
    # Create buffer if no output path specified
    if output_path is None:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
    else:
        doc = SimpleDocTemplate(output_path, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # Build story
    story = []
    
    # Title
    story.append(Paragraph("ACCREDITATION FORMS SUMMARY REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Summary table
    table_data = [['Company Name', 'Contact Person', 'Status', 'Submitted Date']]
    
    for form in forms:
        table_data.append([
            form.company_name,
            form.contact_person,
            form.status.replace('_', ' ').title(),
            form.submitted_at.strftime('%m/%d/%Y') if form.submitted_at else 'Draft'
        ])
    
    summary_table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)
    
    if output_path is None:
        buffer.seek(0)
        return buffer
    else:
        return output_path
