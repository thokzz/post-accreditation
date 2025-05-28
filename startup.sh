#!/bin/bash
# startup.sh - Initialize database and create admin user

set -e

echo "🚀 Starting GMA Post Accreditation System..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
until python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host='db',
        database='post_accreditation',
        user='postgres',
        password='Strong_Password_2024'
    )
    conn.close()
    print('Database connection successful!')
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
"; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "✅ Database connection established"

# Initialize database
echo "🗄️  Initializing database schema..."
flask init-db || echo "Database already initialized"

# Create admin user
echo "👤 Creating admin user..."
python -c "
from app import create_app, db
from app.models import User, UserRole
import os

app = create_app()
with app.app_context():
    try:
        # Check if admin already exists
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin = User.query.filter_by(username=admin_username).first()
        
        if not admin:
            admin = User(
                username=admin_username,
                email=os.getenv('ADMIN_EMAIL', 'admin@gmanetwork.com'),
                role=UserRole.ADMINISTRATOR,
                is_active=True
            )
            admin.set_password(os.getenv('ADMIN_PASSWORD', 'Admin_2024_Strong'))
            db.session.add(admin)
            db.session.commit()
            print(f'✅ Admin user {admin.username} created successfully!')
            print(f'📧 Email: {admin.email}')
            print(f'🔑 Password: {os.getenv(\"ADMIN_PASSWORD\", \"Admin_2024_Strong\")}')
        else:
            print(f'ℹ️  Admin user {admin.username} already exists.')
    except Exception as e:
        print(f'❌ Error creating admin user: {e}')
        exit(1)
"

echo "🎉 Initialization complete!"
echo ""
echo "📋 Application Details:"
echo "   🌐 URL: http://localhost:5001"
echo "   👤 Admin Username: ${ADMIN_USERNAME:-admin}"
echo "   📧 Admin Email: ${ADMIN_EMAIL:-admin@gmanetwork.com}"
echo "   🔑 Admin Password: ${ADMIN_PASSWORD:-Admin_2024_Strong}"
echo ""
echo "🚀 Starting application server..."

# Start the application
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
