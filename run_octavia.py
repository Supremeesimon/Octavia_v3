#!/usr/bin/env python3
"""
Octavia v3 Launcher
"""

import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

# Set required environment variables if not set
if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = "octavia-v3"  # Replace with your project ID

if not os.getenv("GOOGLE_CLOUD_LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Import and run main window
from interface.main_window import main

if __name__ == "__main__":
    main()
