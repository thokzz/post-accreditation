#!/bin/bash
# setup_directories.sh - Create necessary directory structure for the application

echo "🔧 Setting up directory structure for GMA Post Accreditation System..."

# Create static file directories
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Create upload directories
mkdir -p uploads/signatures
mkdir -p uploads/software_proofs
mkdir -p uploads/floor_plans
mkdir -p uploads/general

# Create instance directory for Flask
mkdir -p instance

# Create the CSS file
cat > static/css/style.css << 'EOF'
/* Enhanced GMA Post Accreditation System Styles */
/* This file will be populated with the enhanced CSS styles */
EOF

echo "✅ Directory structure created successfully!"
echo ""
echo "📁 Created directories:"
echo "   - static/css/"
echo "   - static/js/"
echo "   - static/images/"
echo "   - uploads/signatures/"
echo "   - uploads/software_proofs/"
echo "   - uploads/floor_plans/"
echo "   - uploads/general/"
echo "   - instance/"
echo ""
echo "📝 Next steps:"
echo "   1. Copy the CSS content to static/css/style.css"
echo "   2. Run 'docker-compose build' to rebuild with new structure"
echo "   3. Run 'docker-compose up' to start the application"
echo ""
echo "🎨 The application will now have enhanced styling!"
