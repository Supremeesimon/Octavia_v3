"""
Code analysis and manipulation tools for Octavia.
"""

import ast
from pathlib import Path
from typing import List, Dict, Optional, Any
from loguru import logger

from .tool_system import tool, ToolCategory, ToolParameter

@tool(
    name="parse_python_file",
    description="Parse a Python file and extract its structure",
    category=ToolCategory.CODE_ANALYSIS,
    parameters=[
        ToolParameter("path", str, "Path to Python file", True),
    ]
)
async def parse_python_file(path: str) -> Dict[str, Any]:
    """Parse a Python file and return its structure"""
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise IsADirectoryError(f"Not a file: {path}")

        # Read and parse the file
        code = path.read_text()
        tree = ast.parse(code)

        # Extract structure
        structure = {
            "imports": [],
            "classes": [],
            "functions": [],
            "globals": []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    structure["imports"].append({
                        "name": name.name,
                        "alias": name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    structure["imports"].append({
                        "name": f"{node.module}.{name.name}",
                        "alias": name.asname
                    })
            elif isinstance(node, ast.ClassDef):
                structure["classes"].append({
                    "name": node.name,
                    "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                    "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                    "lineno": node.lineno
                })
            elif isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                    "lineno": node.lineno
                })
            elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                structure["globals"].append({
                    "name": node.targets[0].id,
                    "lineno": node.lineno
                })

        return structure

    except Exception as e:
        logger.error(f"Error parsing Python file {path}: {str(e)}")
        raise

@tool(
    name="find_code_references",
    description="Find references to a symbol in Python files",
    category=ToolCategory.CODE_ANALYSIS,
    parameters=[
        ToolParameter("directory", str, "Directory to search", True),
        ToolParameter("symbol", str, "Symbol to find", True),
        ToolParameter("recursive", bool, "Search recursively", False, True),
    ]
)
async def find_code_references(directory: str, symbol: str, recursive: bool = True) -> List[Dict[str, Any]]:
    """Find references to a symbol in Python files"""
    try:
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        references = []
        pattern = "*.py"
        search_func = directory.rglob if recursive else directory.glob

        class ReferenceVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if node.id == symbol:
                    references.append({
                        "file": str(current_file),
                        "line": node.lineno,
                        "col": node.col_offset,
                        "context": "reference"
                    })
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                if node.name == symbol:
                    references.append({
                        "file": str(current_file),
                        "line": node.lineno,
                        "col": node.col_offset,
                        "context": "class_definition"
                    })
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                if node.name == symbol:
                    references.append({
                        "file": str(current_file),
                        "line": node.lineno,
                        "col": node.col_offset,
                        "context": "function_definition"
                    })
                self.generic_visit(node)

        for py_file in search_func(pattern):
            try:
                code = py_file.read_text()
                tree = ast.parse(code)
                current_file = py_file
                visitor = ReferenceVisitor()
                visitor.visit(tree)
            except Exception as e:
                logger.warning(f"Error parsing {py_file}: {str(e)}")
                continue

        return references

    except Exception as e:
        logger.error(f"Error finding references in {directory}: {str(e)}")
        raise

@tool(
    name="extract_docstrings",
    description="Extract docstrings from a Python file",
    category=ToolCategory.CODE_ANALYSIS,
    parameters=[
        ToolParameter("path", str, "Path to Python file", True),
    ]
)
async def extract_docstrings(path: str) -> Dict[str, str]:
    """Extract docstrings from a Python file"""
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise IsADirectoryError(f"Not a file: {path}")

        # Read and parse the file
        code = path.read_text()
        tree = ast.parse(code)

        docstrings = {
            "module": ast.get_docstring(tree),
            "classes": {},
            "functions": {}
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings["classes"][node.name] = doc
            elif isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings["functions"][node.name] = doc

        return docstrings

    except Exception as e:
        logger.error(f"Error extracting docstrings from {path}: {str(e)}")
        raise
