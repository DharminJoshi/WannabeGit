"""
Enhanced .wannabegitignore pattern matching with gitignore-style rules
"""
import os
import fnmatch
import re
from pathlib import Path
from typing import List, Set

IGNORE_FILE = ".wannabegitignore"

# Default patterns to always ignore
DEFAULT_IGNORE_PATTERNS = [
    ".wannabegit",
    ".wannabegit/*",
    "*.pyc",
    "__pycache__",
    "__pycache__/*",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    "*.swp",
    "*.swo",
    "*~",
    ".*.swp",
]


class IgnorePattern:
    """Represents a single ignore pattern with parsing logic"""
    
    def __init__(self, pattern: str, base_path: str = "."):
        self.original = pattern
        self.negation = pattern.startswith("!")
        self.pattern = pattern[1:] if self.negation else pattern
        self.directory_only = self.pattern.endswith("/")
        self.base_path = base_path
        
        if self.directory_only:
            self.pattern = self.pattern[:-1]
        
        # Convert to regex pattern
        self.is_absolute = self.pattern.startswith("/")
        if self.is_absolute:
            self.pattern = self.pattern[1:]
    
    def matches(self, path: str, is_dir: bool = False) -> bool:
        """Check if path matches this pattern"""
        # Directory-only patterns only match directories
        if self.directory_only and not is_dir:
            return False
        
        # Normalize path
        path = path.replace("\\", "/")
        
        # Handle absolute patterns
        if self.is_absolute:
            return fnmatch.fnmatch(path, self.pattern)
        
        # Check if any part of the path matches
        path_parts = path.split("/")
        pattern_parts = self.pattern.split("/")
        
        # If pattern has no directory separator, match against basename
        if len(pattern_parts) == 1:
            return fnmatch.fnmatch(os.path.basename(path), self.pattern)
        
        # Match full path
        return fnmatch.fnmatch(path, self.pattern) or \
               fnmatch.fnmatch(path, f"**/{self.pattern}")


class IgnoreManager:
    """Manages ignore patterns and file matching"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = repo_root
        self.patterns: List[IgnorePattern] = []
        self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns from .wannabegitignore file"""
        # Start with default patterns
        for pattern in DEFAULT_IGNORE_PATTERNS:
            self.patterns.append(IgnorePattern(pattern, self.repo_root))
        
        # Load from file if exists
        ignore_path = os.path.join(self.repo_root, IGNORE_FILE)
        if os.path.exists(ignore_path):
            try:
                with open(ignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith("#"):
                            self.patterns.append(
                                IgnorePattern(line, self.repo_root)
                            )
            except IOError as e:
                print(f"Warning: Could not read {ignore_path}: {e}")
    
    def is_ignored(self, path: str) -> bool:
        """Check if path should be ignored"""
        # Normalize path
        path = os.path.normpath(path)
        is_dir = os.path.isdir(path)
        
        # Make path relative to repo root
        try:
            rel_path = os.path.relpath(path, self.repo_root)
        except ValueError:
            rel_path = path
        
        # Check against patterns
        ignored = False
        for pattern in self.patterns:
            if pattern.matches(rel_path, is_dir):
                ignored = not pattern.negation
        
        return ignored
    
    def filter_files(self, files: List[str]) -> List[str]:
        """Filter out ignored files from list"""
        return [f for f in files if not self.is_ignored(f)]
    
    def get_tracked_files(self, directory: str = ".") -> List[str]:
        """Get all non-ignored files in directory recursively"""
        tracked = []
        
        for root, dirs, files in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self.is_ignored(os.path.join(root, d))]
            
            # Add non-ignored files
            for file in files:
                filepath = os.path.join(root, file)
                if not self.is_ignored(filepath):
                    tracked.append(filepath)
        
        return tracked


def load_ignore_patterns() -> List[str]:
    """Legacy function - load patterns from ignore file"""
    if not os.path.exists(IGNORE_FILE):
        return DEFAULT_IGNORE_PATTERNS.copy()
    
    patterns = DEFAULT_IGNORE_PATTERNS.copy()
    try:
        with open(IGNORE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    except IOError:
        pass
    
    return patterns


def is_ignored(filename: str) -> bool:
    """Legacy function - check if file is ignored"""
    manager = IgnoreManager()
    return manager.is_ignored(filename)


def create_default_ignore_file():
    """Create a default .wannabegitignore file"""
    if os.path.exists(IGNORE_FILE):
        return
    
    content = """# WannabeGit ignore file
# Patterns follow gitignore syntax

# Python
*.pyc
__pycache__/
*.pyo
*.pyd
.Python
*.so

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build artifacts
dist/
build/
*.egg-info/

# Add your custom patterns below
"""
    
    try:
        with open(IGNORE_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created {IGNORE_FILE}")
    except IOError as e:
        print(f"Warning: Could not create {IGNORE_FILE}: {e}")