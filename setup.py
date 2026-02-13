from setuptools import setup, find_packages

setup(
    name="afis_console",
    version="0.1.0",
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
