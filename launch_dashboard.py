#!/usr/bin/env python3
"""
Simple launcher for the NPI Dashboard
This script tries different methods to launch the Streamlit dashboard
"""

import subprocess
import sys
import os

def launch_dashboard():
    # Use the enhanced dashboard if available, otherwise fallback to original
    if os.path.exists("enhanced_npi_dashboard.py"):
        dashboard_file = "enhanced_npi_dashboard.py"
        print("🚀 Using Enhanced Multi-Tab Dashboard")
    else:
        dashboard_file = "npi_dashboard.py"
        print("🚀 Using Original Dashboard")
    
    if not os.path.exists(dashboard_file):
        print(f"❌ Error: {dashboard_file} not found!")
        return False
    
    # Try different methods to launch streamlit
    methods = [
        ["python3", "-m", "streamlit", "run", dashboard_file],
        ["python", "-m", "streamlit", "run", dashboard_file],
        ["streamlit", "run", dashboard_file],
    ]
    
    for method in methods:
        try:
            print(f"🚀 Trying: {' '.join(method)}")
            subprocess.run(method, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Method failed: {e}")
            continue
    
    print("\n❌ All methods failed!")
    print("\n📋 Manual Instructions:")
    print("1. Open your terminal")
    print("2. Navigate to this directory")
    print("3. Try one of these commands:")
    print("   • python3 -m streamlit run npi_dashboard.py")
    print("   • python -m streamlit run npi_dashboard.py")
    print("   • streamlit run npi_dashboard.py")
    print("\n4. If none work, you may need to install streamlit:")
    print("   • pip3 install streamlit")
    print("   • or pip install streamlit")
    
    return False

if __name__ == "__main__":
    print("🏥 NPI Dashboard Launcher")
    print("=" * 30)
    launch_dashboard() 