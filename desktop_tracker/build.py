"""
LifeOS Desktop Agent — PyInstaller Build Script
Run this script to package the tracker into a standalone Windows .exe.
"""

import os
import subprocess
import sys

def main():
    print("Building LifeOS Desktop Tracker...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Error: PyInstaller is not installed. Run 'pip install pyinstaller'.")
        sys.exit(1)

    # Build command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--windowed",                 # Hide the console window
        "--onefile",                  # Package into a single .exe
        "--name", "LifeOS_Tracker",   # The output name
        "gui_app.py"                  # Entry point
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\nBuild successful!")
        print("Your executable is located at: ./dist/LifeOS_Tracker.exe")
    else:
        print("\nBuild failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
