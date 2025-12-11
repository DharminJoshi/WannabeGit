"""
Core repository management utilities with improved architecture
"""
import os
import json
import hashlib
import zlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Repository structure
VCS_DIR = ".wannabegit"
OBJECTS_DIR = os.path.join(VCS_DIR, "objects")
COMMITS_DIR = os.path.join(VCS_DIR, "commits")
INDEX_FILE = os.path.join(VCS_DIR, "index.json")
HEAD_FILE = os.path.join(VCS_DIR, "HEAD")
REFS_DIR = os.path.join(VCS_DIR, "refs", "heads")
CONFIG_FILE = os.path.join(VCS_DIR, "config.json")


class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass


class Repository:
    """Main repository class for managing VCS operations"""
    
    def __init__(self, path: str = "."):
        self.root = Path(path).resolve()
        self.vcs_dir = self.root / VCS_DIR
        self.objects_dir = self.vcs_dir / "objects"
        self.commits_dir = self.vcs_dir / "commits"
        self.refs_dir = self.vcs_dir / "refs" / "heads"
        
    def exists(self) -> bool:
        """Check if repository is initialized"""
        return self.vcs_dir.exists() and self.vcs_dir.is_dir()
    
    def ensure_exists(self):
        """Ensure repository exists, raise error if not"""
        if not self.exists():
            raise RepositoryError(
                "Not a wannabegit repository. Run 'wannabegit init' first."
            )
    
    def get_head(self) -> Optional[str]:
        """Get current HEAD commit ID or branch reference"""
        head_file = self.vcs_dir / "HEAD"
        if not head_file.exists():
            return None
        
        content = head_file.read_text().strip()
        
        # Check if HEAD is detached (direct commit) or symbolic (branch)
        if content.startswith("ref: "):
            # Symbolic reference to branch
            ref_path = content[5:]  # Remove "ref: " prefix
            ref_file = self.vcs_dir / ref_path
            if ref_file.exists():
                return ref_file.read_text().strip()
            return None
        
        return content if content else None
    
    def set_head(self, commit_id: str, branch: Optional[str] = None):
        """Set HEAD to commit or branch"""
        head_file = self.vcs_dir / "HEAD"
        
        if branch:
            # Symbolic reference
            head_file.write_text(f"ref: refs/heads/{branch}\n")
            # Update branch reference
            branch_file = self.refs_dir / branch
            branch_file.write_text(f"{commit_id}\n")
        else:
            # Detached HEAD
            head_file.write_text(f"{commit_id}\n")
    
    def get_current_branch(self) -> Optional[str]:
        """Get name of current branch"""
        head_file = self.vcs_dir / "HEAD"
        if not head_file.exists():
            return None
        
        content = head_file.read_text().strip()
        if content.startswith("ref: refs/heads/"):
            return content[16:]  # Remove "ref: refs/heads/"
        
        return None  # Detached HEAD
    
    def list_branches(self) -> List[str]:
        """List all branches"""
        if not self.refs_dir.exists():
            return []
        return [f.name for f in self.refs_dir.iterdir() if f.is_file()]
    
    def branch_exists(self, name: str) -> bool:
        """Check if branch exists"""
        return (self.refs_dir / name).exists()
    
    def get_config(self) -> Dict[str, Any]:
        """Load repository configuration"""
        config_path = self.vcs_dir / "config.json"
        if not config_path.exists():
            return {
                "user": {
                    "name": os.environ.get("USER", "Unknown"),
                    "email": "user@localhost"
                }
            }
        return json.loads(config_path.read_text())
    
    def save_config(self, config: Dict[str, Any]):
        """Save repository configuration"""
        config_path = self.vcs_dir / "config.json"
        config_path.write_text(json.dumps(config, indent=2))


def ensure_vcs_exists():
    """Legacy function for backward compatibility"""
    repo = Repository()
    repo.ensure_exists()


def read_json(path: str, default: Any) -> Any:
    """Read JSON file with default fallback"""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read {path}: {e}")
        return default


def write_json(path: str, data: Any):
    """Write JSON file with proper formatting"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add trailing newline


def generate_commit_id(message: str, timestamp: str, parent: Optional[str] = None) -> str:
    """Generate unique commit ID using SHA-1 hash"""
    content = f"{message}|{timestamp}|{parent or 'root'}"
    return hashlib.sha1(content.encode("utf-8")).hexdigest()[:8]


def hash_file_content(content: bytes) -> str:
    """Generate hash for file content"""
    return hashlib.sha1(content).hexdigest()


def compress_content(content: bytes) -> bytes:
    """Compress content using zlib"""
    return zlib.compress(content)


def decompress_content(content: bytes) -> bytes:
    """Decompress zlib content"""
    return zlib.decompress(content)


def get_file_hash(file_path: str) -> str:
    """Get hash of file content"""
    try:
        with open(file_path, "rb") as f:
            return hash_file_content(f.read())
    except IOError:
        return ""


def write_head(commit_id: str):
    """Legacy function - write commit ID to HEAD"""
    repo = Repository()
    current_branch = repo.get_current_branch()
    repo.set_head(commit_id, current_branch)


def get_relative_path(file_path: str) -> str:
    """Get path relative to repository root"""
    try:
        return os.path.relpath(file_path)
    except ValueError:
        return file_path


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format timestamp in consistent format"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string"""
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")