"""
Global state management for Octavia
"""

class OctaviaState:
    def __init__(self):
        self.current_project = None
        self.current_workspace = None
        self.workspaces = []
        self.projects = {}
