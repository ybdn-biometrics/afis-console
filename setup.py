from setuptools import setup, find_packages
import re

# Read version from __init__.py (single source of truth)
with open("src/afis_console/__init__.py", "r") as f:
    version = re.search(r'__version__\s*=\s*"(.+?)"', f.read()).group(1)

setup(
    name="afis_console",
    version=version,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "customtkinter",
        "pymupdf",
        "packaging"
    ],
    entry_points={
        "console_scripts": [
            "afis-console=afis_console.main:main",
        ],
    },
)
