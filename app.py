import os
from app import create_app, db, celery
from app.models import User, AccreditationForm, Approval, AuditLog, SystemConfiguration
from flask_migrate import upgrade
from app.utils.email import send_welcome_email

# Create Flask application - THIS IS THE KEY LINE
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Configure Celery
celery.conf.update(app.config['CELERY'])

@app.shell_context_processor
def make_shell_context():
    """Make database models available in shell context"""
    return {
        'db': db,
        'User': User,
        'AccreditationForm': AccreditationForm,
        'Approval': Approval,
        'AuditLog': AuditLog,
        'SystemConfiguration': SystemConfiguration
    }

@app.cli.command()
def deploy():
    """Deploy the application"""
    # Create database tables
    upgrade()
    
    # Create default system configurations
    create_default_configs()
    
    # Create default admin user if it doesn't exist
    create_default_admin()

def create_default_configs():
    """Create default system configurations"""
    default_configs = [
        {
            'key': 'site_name',
            'value': 'Post Accreditation System',
            'description': 'Name of the application',
            'category': 'general',
            'is_public': True,
            'is_system': True
        },
        {
            'key': 'admin_email',
            'value': 'admin@postaccreditation.com',
            'description': 'Administrator email address',
            'category': 'email',
            'is_system': True
        },
        {
            'key': 'max_file_size_mb',
            'value': '16',
            'data_type': 'integer',
            'description': 'Maximum file upload size in MB',
            'category': 'uploads',
            'is_system': True
        },
        {
            'key': 'form_link_expiration_days',
            'value': '0',
            'data_type': 'integer',
            'description': 'Form link expiration in days (0 = never expires)',
            'category': 'forms',
            'is_system': True
        },
        {
            'key': 'require_2fa',
            'value': 'false',
            'data_type': 'boolean',
            'description': 'Require 2FA for all users',
            'category': 'security',
            'is_system': True
        },
        {
            'key': 'auto_approve_threshold',
            'value': '0',
            'data_type': 'integer',
            'description': 'Auto-approve forms after X days (0 = disabled)',
            'category': 'workflow'
        },
        {
            'key': 'notification_enabled',
            'value': 'true',
            'data_type': 'boolean',
            'description': 'Enable email notifications',
            'category': 'email',
            'is_public': True
        }
    ]
    
    for config_data in default_configs:
        existing = SystemConfiguration.query.filter_by(key=config_data['key']).first()
        if not existing:
            config = SystemConfiguration(**config_data)
            db.session.add(config)
    
    db.session.commit()

def create_default_admin():
    """Create default administrator user"""
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@postaccreditation.com',
            first_name='System',
            last_name='Administrator',
            role='administrator',
            is_active=True,
            email_confirmed=True
        )
        admin.set_password('admin123')  # Change this in production!
        
        db.session.add(admin)
        db.session.commit()
        
        print("Default admin user created:")
        print("Username: admin")
        print("Password: admin123")
        print("Please change the password immediately!")
        
        # Log the creation
        AuditLog.log_user_action(
            action='admin_user_created',
            target_user=admin,
            description="Default admin user created during deployment"
        )

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    create_default_configs()
    create_default_admin()
    print("Database initialized successfully!")

@app.cli.command()
def create_admin():
    """Create an administrator user"""
    import getpass
    
    username = input("Username: ")
    email = input("Email: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        return
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f"User with username '{username}' already exists!")
        return
    
    if User.query.filter_by(email=email).first():
        print(f"User with email '{email}' already exists!")
        return
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='administrator',
        is_active=True,
        email_confirmed=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Administrator user '{username}' created successfully!")

@app.cli.command()
def create_user():
    """Create a regular user"""
    import getpass
    
    username = input("Username: ")
    email = input("Email: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    
    print("Available roles:")
    print("1. viewer")
    print("2. approver") 
    print("3. manager")
    print("4. administrator")
    
    role_choice = input("Select role (1-4): ")
    role_map = {'1': 'viewer', '2': 'approver', '3': 'manager', '4': 'administrator'}
    role = role_map.get(role_choice, 'viewer')
    
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        return
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f"User with username '{username}' already exists!")
        return
    
    if User.query.filter_by(email=email).first():
        print(f"User with email '{email}' already exists!")
        return
    
    # Create user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_active=True,
        email_confirmed=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f"User '{username}' with role '{role}' created successfully!")

@app.cli.command()
def cleanup_files():
    """Clean up orphaned files"""
    from app.utils.file_handler import cleanup_orphaned_files
    
    result = cleanup_orphaned_files()
    print(f"Found {result['orphaned_count']} orphaned files")
    print(f"Deleted {result['deleted_count']} files")

@app.cli.command()
def test_email():
    """Test email configuration"""
    from app.utils.email import send_email
    
    recipient = input("Test email recipient: ")
    
    result = send_email(
        subject="Test Email - Post Accreditation System",
        recipients=[recipient],
        text_body="This is a test email to verify email configuration.",
        html_body="<h3>Test Email</h3><p>This is a test email to verify email configuration.</p>",
        async_send=False
    )
    
    if result:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email. Check your email configuration.")

@app.cli.command()
def audit_stats():
    """Show audit log statistics"""
    from sqlalchemy import func
    
    # Total audit logs
    total_logs = AuditLog.query.count()
    print(f"Total audit logs: {total_logs}")
    
    # Logs by action
    action_stats = db.session.query(
        AuditLog.action,
        func.count(AuditLog.id)
    ).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc()).all()
    
    print("\nTop actions:")
    for action, count in action_stats[:10]:
        print(f"  {action}: {count}")
    
    # Logs by risk level
    risk_stats = db.session.query(
        AuditLog.risk_level,
        func.count(AuditLog.id)
    ).group_by(AuditLog.risk_level).all()
    
    print("\nRisk levels:")
    for risk, count in risk_stats:
        print(f"  {risk}: {count}")

# This is needed for Flask CLI commands
if __name__ == '__main__':
    app.run(debug=True)

# Configure Celery
celery.conf.update(app.config['CELERY'])

@app.shell_context_processor
def make_shell_context():
    """Make database models available in shell context"""
    return {
        'db': db,
        'User': User,
        'AccreditationForm': AccreditationForm,
        'Approval': Approval,
        'AuditLog': AuditLog,
        'SystemConfiguration': SystemConfiguration
    }

@app.cli.command()
def deploy():
    """Deploy the application"""
    # Create database tables
    upgrade()
    
    # Create default system configurations
    create_default_configs()
    
    # Create default admin user if it doesn't exist
    create_default_admin()

def create_default_configs():
    """Create default system configurations"""
    default_configs = [
        {
            'key': 'site_name',
            'value': 'Post Accreditation System',
            'description': 'Name of the application',
            'category': 'general',
            'is_public': True,
            'is_system': True
        },
        {
            'key': 'admin_email',
            'value': 'admin@postaccreditation.com',
            'description': 'Administrator email address',
            'category': 'email',
            'is_system': True
        },
        {
            'key': 'max_file_size_mb',
            'value': '16',
            'data_type': 'integer',
            'description': 'Maximum file upload size in MB',
            'category': 'uploads',
            'is_system': True
        },
        {
            'key': 'form_link_expiration_days',
            'value': '0',
            'data_type': 'integer',
            'description': 'Form link expiration in days (0 = never expires)',
            'category': 'forms',
            'is_system': True
        },
        {
            'key': 'require_2fa',
            'value': 'false',
            'data_type': 'boolean',
            'description': 'Require 2FA for all users',
            'category': 'security',
            'is_system': True
        },
        {
            'key': 'auto_approve_threshold',
            'value': '0',
            'data_type': 'integer',
            'description': 'Auto-approve forms after X days (0 = disabled)',
            'category': 'workflow'
        },
        {
            'key': 'notification_enabled',
            'value': 'true',
            'data_type': 'boolean',
            'description': 'Enable email notifications',
            'category': 'email',
            'is_public': True
        }
    ]
    
    for config_data in default_configs:
        existing = SystemConfiguration.query.filter_by(key=config_data['key']).first()
        if not existing:
            config = SystemConfiguration(**config_data)
            db.session.add(config)
    
    db.session.commit()

def create_default_admin():
    """Create default administrator user"""
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@postaccreditation.com',
            first_name='System',
            last_name='Administrator',
            role='administrator',
            is_active=True,
            email_confirmed=True
        )
        admin.set_password('admin123')  # Change this in production!
        
        db.session.add(admin)
        db.session.commit()
        
        print("Default admin user created:")
        print("Username: admin")
        print("Password: admin123")
        print("Please change the password immediately!")
        
        # Log the creation
        AuditLog.log_user_action(
            action='admin_user_created',
            target_user=admin,
            description="Default admin user created during deployment"
        )

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    create_default_configs()
    create_default_admin()
    print("Database initialized successfully!")

@app.cli.command()
def create_admin():
    """Create an administrator user"""
    import getpass
    
    username = input("Username: ")
    email = input("Email: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        return
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f"User with username '{username}' already exists!")
        return
    
    if User.query.filter_by(email=email).first():
        print(f"User with email '{email}' already exists!")
        return
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='administrator',
        is_active=True,
        email_confirmed=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Administrator user '{username}' created successfully!")

@app.cli.command()
def create_user():
    """Create a regular user"""
    import getpass
    
    username = input("Username: ")
    email = input("Email: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    
    print("Available roles:")
    print("1. viewer")
    print("2. approver") 
    print("3. manager")
    print("4. administrator")
    
    role_choice = input("Select role (1-4): ")
    role_map = {'1': 'viewer', '2': 'approver', '3': 'manager', '4': 'administrator'}
    role = role_map.get(role_choice, 'viewer')
    
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        return
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f"User with username '{username}' already exists!")
        return
    
    if User.query.filter_by(email=email).first():
        print(f"User with email '{email}' already exists!")
        return
    
    # Create user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_active=True,
        email_confirmed=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f"User '{username}' with role '{role}' created successfully!")

@app.cli.command()
def cleanup_files():
    """Clean up orphaned files"""
    from app.utils.file_handler import cleanup_orphaned_files
    
    result = cleanup_orphaned_files()
    print(f"Found {result['orphaned_count']} orphaned files")
    print(f"Deleted {result['deleted_count']} files")

@app.cli.command()
def test_email():
    """Test email configuration"""
    from app.utils.email import send_email
    
    recipient = input("Test email recipient: ")
    
    result = send_email(
        subject="Test Email - Post Accreditation System",
        recipients=[recipient],
        text_body="This is a test email to verify email configuration.",
        html_body="<h3>Test Email</h3><p>This is a test email to verify email configuration.</p>",
        async_send=False
    )
    
    if result:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email. Check your email configuration.")

@app.cli.command()
def audit_stats():
    """Show audit log statistics"""
    from sqlalchemy import func
    
    # Total audit logs
    total_logs = AuditLog.query.count()
    print(f"Total audit logs: {total_logs}")
    
    # Logs by action
    action_stats = db.session.query(
        AuditLog.action,
        func.count(AuditLog.id)
    ).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc()).all()
    
    print("\nTop actions:")
    for action, count in action_stats[:10]:
        print(f"  {action}: {count}")
    
    # Logs by risk level
    risk_stats = db.session.query(
        AuditLog.risk_level,
        func.count(AuditLog.id)
    ).group_by(AuditLog.risk_level).all()
    
    print("\nRisk levels:")
    for risk, count in risk_stats:
        print(f"  {risk}: {count}")

if __name__ == '__main__':
    app.run(debug=True)