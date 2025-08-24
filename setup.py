#!/usr/bin/env python3
"""
Setup script for the CrewAI Deep Research Agent.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a shell command with error handling."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   This project requires Python 3.8 or higher")
        return False


def install_dependencies():
    """Install required Python packages."""
    return run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    )


def test_installation():
    """Test if the installation works."""
    return run_command(
        "python test_api.py",
        "Testing API integration"
    )


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        try:
            with open('env_example.txt', 'r') as template:
                content = template.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ .env file created")
            print("⚠️  Please edit .env file and add your API keys!")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
        return True


def main():
    """Main setup function."""
    print("🚀 CrewAI Deep Research Agent Setup")
    print("=" * 50)
    
    setup_steps = [
        ("Python Version Check", check_python_version),
        ("Dependency Installation", install_dependencies),
        ("Environment File Setup", create_env_file),
        ("Installation Test", test_installation)
    ]
    
    results = []
    
    for step_name, step_func in setup_steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 30)
        result = step_func()
        results.append((step_name, result))
        
        if not result:
            print(f"\n❌ Setup failed at step: {step_name}")
            break
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    
    for step_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"  {status} - {step_name}")
    
    if all(result for _, result in results):
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file and add your OPENAI_API_KEY")
        print("2. Run: python main.py")
        print("3. Start researching!")
    else:
        print("\n⚠️  Setup incomplete. Please resolve the issues above.")


if __name__ == "__main__":
    main()
