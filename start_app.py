import sys
import os

# Add src to Python path to allow running without installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from afis_console.main import main

if __name__ == "__main__":
    main()
