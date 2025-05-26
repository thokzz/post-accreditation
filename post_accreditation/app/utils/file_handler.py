import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import mimetypes
from PIL import Image
import hashlib

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def generate_unique_filename(original_filename):
    """Generate unique filename while preserving extension"""
    extension = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{extension}" if extension else unique_id

def get_file_hash(file_path):
    """Generate SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0

def create_upload_directory(subdirectory=None):
    """Create upload directory if it doesn't exist"""
    base_path = current_app.config['UPLOAD_FOLDER']
    
    if subdirectory:
        upload_path = os.path.join(base_path, subdirectory)
    else:
        upload_path = base_path
    
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def save_uploaded_file(file, subdirectory=None, custom_filename=None, allowed_extensions=None):
    """
    Save uploaded file to designated directory
    
    Args:
        file: FileStorage object
        subdirectory: Subdirectory within upload folder
        custom_filename: Custom filename (without extension)
        allowed_extensions: Set of allowed file extensions
    
    Returns:
        dict: File information including path, filename, size, etc.
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename, allowed_extensions):
        raise ValueError(f"File type not allowed. Allowed types: {allowed_extensions or current_app.config['ALLOWED_EXTENSIONS']}")
    
    # Create upload directory
    upload_dir = create_upload_directory(subdirectory)
    
    # Generate filename
    original_filename = secure_filename(file.filename)
    if custom_filename:
        extension = get_file_extension(original_filename)
        filename = f"{secure_filename(custom_filename)}.{extension}" if extension else secure_filename(custom_filename)
    else:
        filename = generate_unique_filename(original_filename)
    
    # Full file path
    file_path = os.path.join(upload_dir, filename)
    
    # Check if file already exists
    counter = 1
    base_filename = filename
    while os.path.exists(file_path):
        name, ext = os.path.splitext(base_filename)
        filename = f"{name}_{counter}{ext}"
        file_path = os.path.join(upload_dir, filename)
        counter += 1
    
    # Save file
    file.save(file_path)
    
    # Get file information
    file_info = {
        'filename': filename,
        'original_filename': original_filename,
        'file_path': file_path,
        'relative_path': os.path.relpath(file_path, current_app.config['UPLOAD_FOLDER']),
        'file_size': get_file_size(file_path),
        'mime_type': mimetypes.guess_type(file_path)[0],
        'file_hash': get_file_hash(file_path),
        'subdirectory': subdirectory
    }
    
    # Additional processing for images
    if file_info['mime_type'] and file_info['mime_type'].startswith('image/'):
        try:
            with Image.open(file_path) as img:
                file_info['image_width'] = img.width
                file_info['image_height'] = img.height
                file_info['image_format'] = img.format
        except Exception:
            # Not a valid image or unsupported format
            pass
    
    return file_info

def delete_file(file_path):
    """Delete file from filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
    return False

def get_upload_url(relative_path):
    """Get URL for uploaded file"""
    return f"/uploads/{relative_path}"

def validate_image_file(file, max_size_mb=5, allowed_formats=None):
    """
    Validate image file
    
    Args:
        file: FileStorage object
        max_size_mb: Maximum file size in MB
        allowed_formats: List of allowed image formats
    
    Returns:
        dict: Validation result with success status and error message
    """
    if allowed_formats is None:
        allowed_formats = ['PNG', 'JPEG', 'JPG', 'GIF']
    
    try:
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > max_size_mb * 1024 * 1024:
            return {
                'success': False,
                'error': f'File size exceeds {max_size_mb}MB limit'
            }
        
        # Check if it's a valid image
        try:
            img = Image.open(file)
            img.verify()
            file.seek(0)  # Reset file pointer
            
            if img.format not in allowed_formats:
                return {
                    'success': False,
                    'error': f'Image format not allowed. Allowed formats: {", ".join(allowed_formats)}'
                }
            
            return {
                'success': True,
                'width': img.width,
                'height': img.height,
                'format': img.format
            }
            
        except Exception:
            return {
                'success': False,
                'error': 'Invalid image file'
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Error validating file: {str(e)}'
        }

def create_thumbnail(image_path, thumbnail_path, size=(150, 150)):
    """Create thumbnail from image"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail: {str(e)}")
        return False

def get_file_type_category(mime_type):
    """Categorize file by MIME type"""
    if not mime_type:
        return 'unknown'
    
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf']:
        return 'document'
    elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']:
        return 'archive'
    elif mime_type.startswith('text/'):
        return 'text'
    else:
        return 'other'

def organize_files_by_form(form_id):
    """Organize uploaded files into form-specific directory"""
    subdirectory = f"forms/{form_id}"
    return create_upload_directory(subdirectory)

def cleanup_orphaned_files():
    """Clean up files that are no longer referenced in database"""
    from app.models import FormAttachment
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    orphaned_files = []
    
    # Get all files in upload directory
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, upload_folder)
            
            # Check if file is referenced in database
            attachment = FormAttachment.query.filter_by(file_path=file_path).first()
            if not attachment:
                orphaned_files.append(file_path)
    
    # Delete orphaned files (in production, move to quarantine first)
    deleted_count = 0
    for file_path in orphaned_files:
        if delete_file(file_path):
            deleted_count += 1
    
    return {
        'orphaned_count': len(orphaned_files),
        'deleted_count': deleted_count
    }
