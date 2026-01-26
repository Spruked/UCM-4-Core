#!/usr/bin/env python3
"""
ORB_X Setup Script
Automated setup for the ORB_X desktop control interface
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and print status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Output: {e.output}")
        return False

def main():
    """Main setup function"""
    print("🚀 ORB_X Setup - Desktop Control Interface")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)

    print(f"✅ Python {sys.version.split()[0]} detected")

    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)

    # Test PySide6 import
    try:
        import PySide6.QtWidgets
        print("✅ PySide6 installed successfully")
    except ImportError:
        print("❌ PySide6 import failed")
        sys.exit(1)

    # Test UCM connection
    print("\n🔗 Testing UCM connection...")
    try:
        import requests
        response = requests.get("http://localhost:5050/health", timeout=5)
        if response.status_code == 200:
            print("✅ UCM service detected")
        else:
            print(f"⚠️  UCM service responded with status {response.status_code}")
    except requests.exceptions.RequestException:
        print("⚠️  UCM service not detected (this is OK if not running)")

    print("\n🎯 ORB_X Setup Complete!")
    print("Launch with: python orb_x.py")
    print("Test connection: python test_connection.py")

if __name__ == "__main__":
    main()