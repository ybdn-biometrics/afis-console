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
    '--onefile',
    '--noconsole',
    f'--add-data={ctk_path}{sep}customtkinter',
    '--paths=src',
    '--clean',
    '--log-level=INFO',
]

# Run PyInstaller
try:
    PyInstaller.__main__.run(args)
except Exception as e:
    print(f"Build failed: {e}")
    sys.exit(1)
