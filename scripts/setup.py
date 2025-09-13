#!/usr/bin/env python3
"""Quick setup script for Vulna."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and show result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Vulna Quick Setup")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not Path("backend/main.py").exists():
        print("❌ Please run this script from the Vulna root directory")
        sys.exit(1)
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browsers"):
        print("⚠️  Playwright installation failed, but continuing...")
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    print("✅ Created data directory")
    
    # Check Ollama
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama found")
            
            # Check if llama3.2 is available
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "llama3.2" in result.stdout:
                print("✅ llama3.2 model found")
            else:
                print("🔄 Downloading llama3.2 model...")
                run_command("ollama pull llama3.2", "Downloading llama3.2")
        else:
            print("❌ Ollama not found")
            print("   Install from: https://ollama.ai")
    except FileNotFoundError:
        print("❌ Ollama not found")
        print("   Install from: https://ollama.ai")
    
    print("\n" + "=" * 30)
    print("🎯 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Install Ollama if missing: https://ollama.ai")
    print("2. Run: ollama pull llama3.2")
    print("3. Start Vulna: python -m backend.main")
    print("4. Install HTTPS certs: python scripts/install_certificates.py")


if __name__ == "__main__":
    main()
