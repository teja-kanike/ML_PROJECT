#!/usr/bin/env python3
"""
Fixed ML Setup Script - Handles dependencies properly
"""

import os
import sys
import subprocess
import importlib

def check_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf', 
        'wtforms', 'mysql.connector', 'sklearn', 'pandas', 'numpy',
        'matplotlib', 'seaborn', 'textblob', 'nltk', 'joblib',
        'werkzeug', 'bcrypt', 'email_validator', 'reportlab'
    ]
    
    print("🔍 Checking dependencies...")
    
    for package in required_packages:
        try:
            # Handle different import names
            if package == 'sklearn':
                import_name = 'sklearn'
            elif package == 'mysql.connector':
                import_name = 'mysql.connector'
            else:
                import_name = package.replace('_', '-')
            
            importlib.import_module(import_name)
            print(f"✅ {package}")
            
        except ImportError:
            print(f"❌ {package} - Installing...")
            try:
                # Install using pip
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")

def setup_directories():
    """Create necessary directories"""
    directories = [
        'ml_models/trained_models',
        'logs',
        'uploads/student_documents',
        'uploads/complaint_photos', 
        'uploads/reports',
        'static/css',
        'static/js',
        'static/images',
        'static/vendors',
        'templates/auth',
        'templates/student',
        'templates/admin',
        'templates/warden',
        'database',
        'utils',
        'models',
        'routes',
        'forms',
        'tests',
        'docs'
    ]
    
    print("\n📁 Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def train_models():
    """Train ML models using standalone script"""
    print("\n🤖 Training ML models...")
    try:
        # Run the standalone training script
        subprocess.check_call([sys.executable, 'train_ml_models_standalone.py'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error training models: {e}")
        return False

def main():
    """Main setup function"""
    print("🎯 Hostel Management System - ML Setup")
    print("=" * 50)
    
    # Check and install dependencies
    check_dependencies()
    
    # Create directories
    setup_directories()
    
    # Train ML models
    success = train_models()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Setup MySQL database using: python database/setup_database.py")
        print("2. Run the application: python run.py")
        print("3. Access at: http://localhost:5000")
        print("4. Admin login: admin / admin123")
    else:
        print("\n❌ Setup failed! Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()