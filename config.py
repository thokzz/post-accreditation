import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost/post_accreditation'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # External URL for link generation
    EXTERNAL_URL = os.environ.get('EXTERNAL_URL') or 'http://0.0.0.0:5001'
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@gmanetwork.com'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Timezone
    TIMEZONE = os.environ.get('TIMEZONE') or 'Asia/Manila'

class DevelopmentConfig(Config):
    DEBUG = True
    EXTERNAL_URL = os.environ.get('EXTERNAL_URL') or 'http://localhost:5001'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    EXTERNAL_URL = 'http://localhost:5000'

class ProductionConfig(Config):
    DEBUG = False
    EXTERNAL_URL = os.environ.get('EXTERNAL_URL') or 'https://your-domain.com'
