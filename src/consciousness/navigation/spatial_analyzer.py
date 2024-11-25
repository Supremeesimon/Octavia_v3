"""
Spatial Analysis Module for Octavia - Handles spatial understanding and visualization of filesystem
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict
from datetime import datetime
import mimetypes
from loguru import logger
import time

class SpatialAnalyzer:
    """Analyzes and visualizes filesystem spatial relationships"""
    
    def __init__(self):
        """Initialize the spatial analyzer"""
        self.spatial_map = {}
        self.relationship_graph = defaultdict(list)
        self.access_patterns = defaultdict(int)
        self.file_clusters = defaultdict(list)
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes cache timeout
        
    def analyze_directory_structure(self, root_path: str) -> Dict[str, Any]:
        """Create a spatial map of directory structure"""
        try:
            # Check cache first
            cache_key = f"{root_path}_{int(time.time() / self._cache_timeout)}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Quick check if analysis is needed
            root = Path(root_path)
            if not root.exists():
                return {}
                
            # Do lightweight analysis first
            structure = {
                "name": root.name,
                "type": "directory",
                "path": str(root),
                "depth": len(root.parts),
                "children": [],
                "metadata": {
                    "last_modified": datetime.fromtimestamp(root.stat().st_mtime).isoformat(),
                }
            }
            
            # Only do deep analysis for smaller directories
            dir_size = sum(1 for _ in root.rglob('*'))
            if dir_size > 1000:  # If directory is too large
                structure["metadata"]["size"] = "large"
                structure["metadata"]["num_files"] = dir_size
                # Only analyze immediate children
                for item in root.iterdir():
                    structure["children"].append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "path": str(item)
                    })
            else:
                # Full analysis for manageable directories
                structure["metadata"].update({
                    "size": sum(f.stat().st_size for f in root.rglob('*') if f.is_file()),
                    "num_files": dir_size
                })
                for item in root.iterdir():
                    if item.is_dir():
                        structure["children"].append(self.analyze_directory_structure(str(item)))
                    else:
                        structure["children"].append({
                            "name": item.name,
                            "type": "file",
                            "path": str(item),
                            "depth": len(item.parts),
                            "metadata": {
                                "last_modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                                "size": item.stat().st_size,
                                "mime_type": mimetypes.guess_type(item.name)[0]
                            }
                        })
            
            # Cache the result
            self._cache[cache_key] = structure
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing directory structure: {e}")
            return {}
    
    def identify_clusters(self, root_path: str) -> Dict[str, List[str]]:
        """Identify clusters of related files based on patterns"""
        try:
            clusters = defaultdict(list)
            root = Path(root_path)
            
            # Group by file type
            for file in root.rglob('*'):
                if file.is_file():
                    mime_type = mimetypes.guess_type(file.name)[0] or "unknown"
                    main_type = mime_type.split('/')[0]
                    clusters[main_type].append(str(file))
            
            # Group by modification time proximity
            time_clusters = defaultdict(list)
            for file in root.rglob('*'):
                if file.is_file():
                    mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                    time_key = mod_time.strftime("%Y-%m-%d")
                    time_clusters[f"modified_{time_key}"].append(str(file))
            
            clusters.update(time_clusters)
            return dict(clusters)
            
        except Exception as e:
            logger.error(f"Error identifying clusters: {str(e)}")
            return {"error": str(e)}
    
    def analyze_spatial_relationships(self, path: str) -> Dict[str, List[str]]:
        """Analyze spatial relationships between files and directories"""
        try:
            relationships = {
                "neighbors": [],  # Files/dirs in same directory
                "related_by_name": [],  # Files with similar names
                "related_by_type": [],  # Files of same type
                "related_by_time": [],  # Files modified around same time
            }
            
            target = Path(path)
            if not target.exists():
                return {"error": f"Path does not exist: {path}"}
            
            # Find neighbors
            if target.parent.exists():
                relationships["neighbors"] = [
                    str(p) for p in target.parent.iterdir() if p != target
                ]
            
            # Find related by name (similar prefixes/suffixes)
            name_pattern = target.stem.split('_')[0]  # Use first part of name
            relationships["related_by_name"] = [
                str(p) for p in target.parent.rglob(f'*{name_pattern}*')
                if p != target
            ]
            
            # Find related by type
            if target.is_file():
                target_type = mimetypes.guess_type(target.name)[0]
                if target_type:
                    main_type = target_type.split('/')[0]
                    relationships["related_by_type"] = [
                        str(p) for p in target.parent.rglob(f'*.{target.suffix}')
                        if p != target
                    ]
            
            # Find related by modification time
            target_time = datetime.fromtimestamp(target.stat().st_mtime)
            time_window = 3600  # 1 hour window
            
            def is_time_related(p: Path) -> bool:
                try:
                    p_time = datetime.fromtimestamp(p.stat().st_mtime)
                    return abs((p_time - target_time).total_seconds()) <= time_window
                except:
                    return False
            
            relationships["related_by_time"] = [
                str(p) for p in target.parent.rglob('*')
                if p != target and is_time_related(p)
            ]
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error analyzing spatial relationships: {str(e)}")
            return {"error": str(e)}
    
    def suggest_reorganization(self, root_path: str) -> Dict[str, Any]:
        """Suggest reorganization based on spatial analysis"""
        try:
            suggestions = {
                "moves": [],  # Suggested file moves
                "new_directories": [],  # Suggested new directories
                "clusters": [],  # Suggested file clusters
            }
            
            root = Path(root_path)
            clusters = self.identify_clusters(str(root))
            
            # Suggest directories for large clusters
            for cluster_type, files in clusters.items():
                if len(files) > 5:  # Threshold for suggesting new directory
                    target_dir = root / f"{cluster_type}_files"
                    suggestions["new_directories"].append(str(target_dir))
                    suggestions["clusters"].append({
                        "type": cluster_type,
                        "files": files,
                        "target_directory": str(target_dir)
                    })
            
            # Analyze file relationships for move suggestions
            for file in root.rglob('*'):
                if file.is_file():
                    relationships = self.analyze_spatial_relationships(str(file))
                    related_files = relationships["related_by_type"] + relationships["related_by_name"]
                    
                    if related_files:
                        # Find most common directory among related files
                        related_dirs = [Path(f).parent for f in related_files]
                        if related_dirs:
                            most_common_dir = max(set(related_dirs), key=related_dirs.count)
                            if most_common_dir != file.parent:
                                suggestions["moves"].append({
                                    "file": str(file),
                                    "target_directory": str(most_common_dir),
                                    "reason": "Related files found in target directory"
                                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating reorganization suggestions: {str(e)}")
            return {"error": str(e)}
    
    def visualize_structure(self, root_path: str) -> str:
        """Create a text-based visualization of directory structure"""
        try:
            def _create_tree(path: Path, prefix: str = "", is_last: bool = True) -> str:
                visualization = ""
                marker = "└── " if is_last else "├── "
                
                visualization += prefix + marker + path.name + "\n"
                
                if path.is_dir():
                    # Sort contents
                    contents = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                    
                    # Calculate new prefix for children
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    
                    # Process all items except the last
                    for item in contents[:-1]:
                        visualization += _create_tree(item, new_prefix, False)
                    
                    # Process the last item
                    if contents:
                        visualization += _create_tree(contents[-1], new_prefix, True)
                
                return visualization
            
            root = Path(root_path)
            return _create_tree(root)
            
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            return f"Error: {str(e)}"
