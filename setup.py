from setuptools import setup

APP = ['src/octavia.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # Changed to False to prevent issues with argv handling
    'packages': [
        'PySide6',
        'google',
        'loguru',
        'aiohttp',
        'google.generativeai',
        'google.auth',
        'google.api_core',
        'vertexai',
        'numpy',
        'sklearn',
        'scipy',
        'qasync',
        'asyncio',
        'sparkle',  # For auto-updates
    ],
    'includes': [
        'google.generativeai',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'sklearn.feature_extraction.text',
        'numpy',
        'asyncio',
        'qasync',
    ],
    'excludes': ['tkinter', 'matplotlib'],
    'plist': {
        'CFBundleName': 'Octavia',
        'CFBundleDisplayName': 'Octavia',
        'CFBundleIdentifier': "com.octavia.app",
        'CFBundleVersion': "3.0.0",
        'CFBundleShortVersionString': "3.0.0",
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'SUFeedURL': 'https://raw.githubusercontent.com/yourusername/octavia/main/appcast.xml',  # Update this URL
        'SUPublicEDKey': '',  # Will be filled after code signing
        'SUEnableAutomaticChecks': True,
        'SUAllowsAutomaticUpdates': True,
    }
}

setup(
    name="octavia",
    version="3.0.0",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
