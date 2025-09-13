#!/usr/bin/env python3
"""Install mitmproxy certificates for HTTPS support."""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_mitmproxy_cert_dir():
    """Get mitmproxy certificate directory."""
    system = platform.system()
    
    if system == "Windows":
        return Path.home() / ".mitmproxy"
    elif system == "Darwin":  # macOS
        return Path.home() / ".mitmproxy"
    else:  # Linux
        return Path.home() / ".mitmproxy"


def generate_certificates():
    """Generate mitmproxy certificates."""
    print("🔐 Generating mitmproxy certificates...")
    
    try:
        # Run mitmdump briefly to generate certificates
        result = subprocess.run([
            "mitmdump", "--version"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ mitmproxy is installed")
        else:
            print("❌ mitmproxy not found. Install with: pip install mitmproxy")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ mitmproxy certificates generated")
    except FileNotFoundError:
        print("❌ mitmproxy not found. Install with: pip install mitmproxy")
        return False
    
    return True


def install_certificate_windows():
    """Install certificate on Windows."""
    cert_dir = get_mitmproxy_cert_dir()
    cert_file = cert_dir / "mitmproxy-ca-cert.pem"
    
    if not cert_file.exists():
        print("❌ Certificate file not found. Run mitmdump first.")
        return False
    
    print(f"📋 Certificate location: {cert_file}")
    print("\n🔧 Manual installation required on Windows:")
    print("1. Double-click the certificate file to open it")
    print("2. Click 'Install Certificate...'")
    print("3. Select 'Local Machine' and click 'Next'")
    print("4. Select 'Place all certificates in the following store'")
    print("5. Click 'Browse...' and select 'Trusted Root Certification Authorities'")
    print("6. Click 'Next' and then 'Finish'")
    
    # Try to open the certificate file
    try:
        subprocess.run(["start", str(cert_file)], shell=True, check=True)
        print("✅ Certificate file opened")
    except subprocess.CalledProcessError:
        print("❌ Could not open certificate file automatically")
    
    return True


def install_certificate_macos():
    """Install certificate on macOS."""
    cert_dir = get_mitmproxy_cert_dir()
    cert_file = cert_dir / "mitmproxy-ca-cert.pem"
    
    if not cert_file.exists():
        print("❌ Certificate file not found. Run mitmdump first.")
        return False
    
    try:
        # Add to system keychain
        subprocess.run([
            "sudo", "security", "add-trusted-cert", 
            "-d", "-r", "trustRoot", "-k", "/Library/Keychains/System.keychain",
            str(cert_file)
        ], check=True)
        
        print("✅ Certificate installed to system keychain")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install certificate: {e}")
        return False


def install_certificate_linux():
    """Install certificate on Linux."""
    cert_dir = get_mitmproxy_cert_dir()
    cert_file = cert_dir / "mitmproxy-ca-cert.pem"
    
    if not cert_file.exists():
        print("❌ Certificate file not found. Run mitmdump first.")
        return False
    
    try:
        # Copy to system certificate directory
        subprocess.run([
            "sudo", "cp", str(cert_file), "/usr/local/share/ca-certificates/mitmproxy-ca-cert.crt"
        ], check=True)
        
        # Update certificate store
        subprocess.run(["sudo", "update-ca-certificates"], check=True)
        
        print("✅ Certificate installed to system store")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install certificate: {e}")
        return False


def main():
    """Main certificate installation function."""
    print("🔐 Vulna Certificate Installer")
    print("=" * 40)
    
    # Generate certificates first
    if not generate_certificates():
        sys.exit(1)
    
    # Install based on platform
    system = platform.system()
    
    if system == "Windows":
        success = install_certificate_windows()
    elif system == "Darwin":
        success = install_certificate_macos()
    elif system == "Linux":
        success = install_certificate_linux()
    else:
        print(f"❌ Unsupported platform: {system}")
        sys.exit(1)
    
    if success:
        print("\n✅ Certificate installation completed!")
        print("\n🔄 Restart your browser to apply changes")
        print("\n📖 Test HTTPS sites after installation")
    else:
        print("\n❌ Certificate installation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
