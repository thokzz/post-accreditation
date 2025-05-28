# run.py - Updated to use simplified version temporarily
#!/usr/bin/env python3
import os
from app import create_app, db
from app.models import User, UserRole
from flask_migrate import upgrade, migrate, init, stamp
from flask.cli import with_appcontext
import click

app = create_app(os.getenv('FLASK_ENV') or 'development')

@app.cli.command()
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, help='Admin password')
def create_admin(username, email, password):
    """Create an admin user."""
    with app.app_context():
        # Check if admin already exists
        if User.query.filter_by(username=username).first():
            click.echo(f'User {username} already exists!')
            return
        
        admin = User(
            username=username,
            email=email,
            role=UserRole.ADMINISTRATOR,
            is_active=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f'Admin user {username} created successfully!')

@app.cli.command()
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        click.echo('Database initialized!')

@app.cli.command()
def reset_db():
    """Reset the database."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        click.echo('Database reset!')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
