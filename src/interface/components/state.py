"""
Global state management for Octavia
"""
from typing import Dict, List, Optional
from PySide6.QtCore import QObject, Signal


class Workspace:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.projects: List[str] = []  # List of project paths in this workspace
        
    def add_project(self, project_path: str):
        if project_path not in self.projects:
            self.projects.append(project_path)
            
    def remove_project(self, project_path: str):
        if project_path in self.projects:
            self.projects.remove(project_path)


class Project:
    def __init__(self, name: str, path: str, workspace: str):
        self.name = name
        self.path = path
        self.workspace = workspace  # Name of parent workspace
        self.files: List[str] = []  # List of file paths in this project
        
    def add_file(self, file_path: str):
        if file_path not in self.files:
            self.files.append(file_path)
            
    def remove_file(self, file_path: str):
        if file_path in self.files:
            self.files.remove(file_path)


class OctaviaState(QObject):
    # Signals for state changes
    workspace_changed = Signal(str)  # Emits workspace name
    project_changed = Signal(str)    # Emits project name
    workspaces_updated = Signal()    # Emits when workspace list changes
    projects_updated = Signal(str)   # Emits workspace name when its projects change
    api_key_changed = Signal(bool)   # Emits when API key status changes
    
    def __init__(self):
        super().__init__()
        self._current_workspace: Optional[str] = None
        self._current_project: Optional[str] = None
        self._workspaces: Dict[str, Workspace] = {}
        self._projects: Dict[str, Project] = {}
        self._api_key: Optional[str] = None
        
    @property
    def current_workspace(self) -> Optional[str]:
        return self._current_workspace
        
    @current_workspace.setter
    def current_workspace(self, workspace_name: Optional[str]):
        if workspace_name != self._current_workspace:
            self._current_workspace = workspace_name
            self._current_project = None  # Reset current project
            self.workspace_changed.emit(workspace_name if workspace_name else "")
            
    @property
    def current_project(self) -> Optional[str]:
        return self._current_project
        
    @current_project.setter
    def current_project(self, project_name: Optional[str]):
        if project_name != self._current_project:
            self._current_project = project_name
            self.project_changed.emit(project_name if project_name else "")
            
    @property
    def api_key(self) -> Optional[str]:
        return self._api_key
        
    @api_key.setter
    def api_key(self, key: Optional[str]):
        if key != self._api_key:
            self._api_key = key
            self.api_key_changed.emit(bool(key))
            
    def add_workspace(self, name: str, path: str) -> bool:
        """Add a new workspace"""
        if name not in self._workspaces:
            self._workspaces[name] = Workspace(name, path)
            self.workspaces_updated.emit()
            return True
        return False
        
    def remove_workspace(self, name: str) -> bool:
        """Remove a workspace and its projects"""
        if name in self._workspaces:
            # Remove all projects in this workspace
            workspace = self._workspaces[name]
            for project_path in workspace.projects:
                if project_path in self._projects:
                    del self._projects[project_path]
            
            # Remove workspace
            del self._workspaces[name]
            
            # Update current selections if needed
            if self._current_workspace == name:
                self.current_workspace = None
                
            self.workspaces_updated.emit()
            return True
        return False
        
    def add_project(self, name: str, path: str, workspace: str) -> bool:
        """Add a new project to a workspace"""
        if workspace in self._workspaces and path not in self._projects:
            self._projects[path] = Project(name, path, workspace)
            self._workspaces[workspace].add_project(path)
            self.projects_updated.emit(workspace)
            return True
        return False
        
    def remove_project(self, path: str) -> bool:
        """Remove a project"""
        if path in self._projects:
            project = self._projects[path]
            workspace = project.workspace
            
            # Remove from workspace
            if workspace in self._workspaces:
                self._workspaces[workspace].remove_project(path)
                
            # Remove project
            del self._projects[path]
            
            # Update current selection if needed
            if self._current_project == path:
                self.current_project = None
                
            self.projects_updated.emit(workspace)
            return True
        return False
        
    def get_workspace_projects(self, workspace: str) -> List[Project]:
        """Get all projects in a workspace"""
        if workspace in self._workspaces:
            return [self._projects[path] 
                   for path in self._workspaces[workspace].projects 
                   if path in self._projects]
        return []
        
    def get_all_workspaces(self) -> List[Workspace]:
        """Get all workspaces"""
        return list(self._workspaces.values())
