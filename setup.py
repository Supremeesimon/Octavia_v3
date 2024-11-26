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
    }
}

setup(
    name="octavia",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
