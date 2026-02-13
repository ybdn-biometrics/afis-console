import PyInstaller.__main__
import customtkinter
import os
import platform
import sys
import shutil

# Add src to path for imports to work during build analysis if not installed
sys.path.insert(0, os.path.abspath("src"))

# Determine OS specific separator
sep = ';' if platform.system() == "Windows" else ':'

# Get customtkinter path
ctk_path = os.path.dirname(customtkinter.__file__)

# Log
print(f"Building for {platform.system()}")
print(f"CustomTkinter path: {ctk_path}")

# Output name
app_name = "TriRapportsFAED"

# PyInstaller arguments
args = [
    'src/afis_console/main.py',
    '--name', app_name,
    '--onedir',   # Changed from --onefile
    '--windowed', # No console window (GUI app)
    f'--add-data={ctk_path}{sep}customtkinter',
    f'--add-data=src/afis_console/assets{sep}afis_console/assets', # Include assets folder
    '--paths=src',
    '--clean',
    '--log-level=INFO',
    '--icon=src/afis_console/assets/app_icon.png', # Add icon
]

# Run PyInstaller
try:
    PyInstaller.__main__.run(args)
except Exception as e:
    print(f"Build failed: {e}")
    sys.exit(1)
