"""
Build Parquet Viewer as single executable

This script creates a standalone .exe file with PyInstaller
"""

import subprocess
import os
from pathlib import Path

def build_executable():
    """Build standalone executable"""
    
    script_path = "parquet_viewer.py"
    output_dir = "dist"
    
    print("=" * 60)
    print("BUILDING PARQUET VIEWER EXECUTABLE")
    print("=" * 60)
    
    # PyInstaller command
    pyinstaller_path = ".venv\\Scripts\\pyinstaller.exe"
    cmd = [
        pyinstaller_path,
        "--onefile",  # Single executable
        "--windowed",  # No console window
        "--name", "ParquetViewer",
        "--add-data", f"parquet_viewer.py:.",
        "--icon", "NONE",  # Or provide .ico file
        script_path
    ]
    
    print(f"\nCommand: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        exe_path = Path(output_dir) / "ParquetViewer.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print("\n" + "=" * 60)
            print("✓ BUILD SUCCESSFUL!")
            print("=" * 60)
            print(f"Executable: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print(f"\nYou can now distribute this .exe to users!")
            print("Users don't need Python installed to run it.")
            return True
        else:
            print("✗ Executable not found!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        print(e.stderr)
        return False

if __name__ == "__main__":
    build_executable()
