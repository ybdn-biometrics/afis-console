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

# Platform-specific suffix
if platform.system() == "Windows":
    app_name_with_suffix = f"{app_name}-Windows"
elif platform.system() == "Linux":
    app_name_with_suffix = f"{app_name}-Linux"
else:
    app_name_with_suffix = app_name

# --- Icon handling ---
# Windows requires .ico format; Linux/macOS can use .png
icon_source = os.path.abspath("src/afis_console/assets/app_icon.png")
icon_arg = None

if os.path.exists(icon_source):
    if platform.system() == "Windows":
        # Convert .png to .ico using Pillow (installed as build dependency)
        ico_path = os.path.abspath("src/afis_console/assets/app_icon.ico")
        try:
            from PIL import Image
            img = Image.open(icon_source)
            # Create .ico with multiple sizes for best Windows rendering
            img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
            icon_arg = f'--icon={ico_path}'
            print(f"[OK] Converted icon to .ico: {ico_path}")
        except Exception as e:
            print(f"[WARN] Could not convert icon to .ico: {e}. Building without icon.")
    else:
        icon_arg = f'--icon={icon_source}'
else:
    print(f"[WARN] Icon not found at {icon_source}. Building without icon.")

# PyInstaller arguments
args = [
    'src/afis_console/main.py',
    '--name', app_name_with_suffix,
    '--onefile',    # Single executable file
    '--windowed',   # No console window (GUI app)
    f'--add-data={ctk_path}{sep}customtkinter',
    f'--add-data=src/afis_console/assets{sep}afis_console/assets',  # Include assets folder
    '--paths=src',
    '--clean',
    '--log-level=INFO',
    '--hidden-import=fitz',
    '--hidden-import=pymupdf',
]

# Add icon if available
if icon_arg:
    args.append(icon_arg)

# Run PyInstaller
try:
    PyInstaller.__main__.run(args)
    print(f"\n[OK] Build successful! Output: dist/{app_name_with_suffix}")
except Exception as e:
    print(f"Build failed: {e}")
    sys.exit(1)
