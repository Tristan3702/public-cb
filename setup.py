#!/usr/bin/env python3
"""
Setup script for Chatty Workers' Compensation Chatbot
Helps configure the environment and test the installation
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'supabase', 'openai', 'python-dotenv', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Please copy env.template to .env and fill in your API keys")
        return False
    
    # Read .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    required_vars = [
        'OPENAI_API_KEY',
        'OPENROUTER_API_KEY', 
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if f'{var}=' not in content or f'{var}=your_' in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("   Please update your .env file with valid API keys")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_configuration():
    """Test the configuration by importing the config module"""
    try:
        from config import Config
        Config.validate()
        print("✅ Configuration validation passed")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False

def create_sample_env():
    """Create a sample .env file from template"""
    if Path('.env').exists():
        print("ℹ️  .env file already exists")
        return
    
    if Path('env.template').exists():
        import shutil
        shutil.copy('env.template', '.env')
        print("✅ Created .env file from template")
        print("   Please edit .env with your actual API keys")
    else:
        print("❌ env.template not found")

def main():
    """Main setup function"""
    print("🏥 Chatty Workers' Compensation Chatbot Setup")
    print("=" * 50)
    
    # Check Python version
    print("\n1. Checking Python version...")
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\n2. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Create .env file if needed
    print("\n3. Checking environment configuration...")
    create_sample_env()
    
    # Check environment variables
    if not check_env_file():
        print("\n📝 To complete setup:")
        print("   1. Copy env.template to .env")
        print("   2. Add your API keys to .env")
        print("   3. Run this setup script again")
        sys.exit(1)
    
    # Test configuration
    print("\n4. Testing configuration...")
    if not test_configuration():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Set up your Supabase database:")
    print("      - Create a new Supabase project")
    print("      - Enable pgvector extension")
    print("      - Run database/schema.sql")
    print("   2. Start the chatbot:")
    print("      streamlit run app.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 