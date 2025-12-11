"""
Enhanced status command with detailed file state tracking
"""
import os
from typing import Dict, List, Set
from wannabegit.core import (
    Repository, INDEX_FILE, COMMITS_DIR, read_json, get_file_hash
)
from wannabegit.ignore import IgnoreManager
from wannabegit.diff_engine import Colors


def get_file_status(file_path: str, staged_files: Dict, 
                   head_commit_path: str = None) -> str:
    """
    Determine file status
    
    Returns:
        'staged', 'modified', 'untracked', 'deleted', 'unchanged'
    """
    if not os.path.exists(file_path):
        if file_path in staged_files:
            return 'staged_deleted'
        return 'deleted'
    
    current_hash = get_file_hash(file_path)
    
    # Check staging area
    if file_path in staged_files:
        staged_hash = staged_files[file_path].get("hash", "")
        if current_hash != staged_hash:
            return 'modified_after_staging'
        return 'staged'
    
    # Check against HEAD if it exists
    if head_commit_path and os.path.exists(head_commit_path):
        rel_path = os.path.relpath(file_path)
        committed_file = os.path.join(head_commit_path, rel_path)
        
        if os.path.exists(committed_file):
            committed_hash = get_file_hash(committed_file)
            if current_hash != committed_hash:
                return 'modified'
            return 'unchanged'
    
    return 'untracked'


def cmd_status(short: bool = False) -> int:
    """
    Display working tree status
    
    Args:
        short: If True, use short format
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Load index
    index = read_json(INDEX_FILE, {
        "tracked_files": [],
        "staged_files": {}
    })
    
    tracked_files = set(index.get("tracked_files", []))
    staged_files = index.get("staged_files", {})
    
    # Get current branch and HEAD
    current_branch = repo.get_current_branch()
    head_commit = repo.get_head()
    head_path = os.path.join(COMMITS_DIR, head_commit) if head_commit else None
    
    # Categorize files
    staged_changes: List[str] = []
    unstaged_changes: List[str] = []
    untracked_files: List[str] = []
    deleted_files: List[str] = []
    
    ignore_manager = IgnoreManager()
    
    # Check tracked files
    for file in tracked_files:
        status = get_file_status(file, staged_files, head_path)
        
        if status == 'staged':
            staged_changes.append(file)
        elif status == 'modified':
            unstaged_changes.append(file)
        elif status == 'deleted':
            deleted_files.append(file)
        elif status == 'modified_after_staging':
            staged_changes.append(file)
            unstaged_changes.append(file)
    
    # Check for untracked files
    for root, dirs, files in os.walk("."):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if not ignore_manager.is_ignored(os.path.join(root, d))]
        
        for file in files:
            filepath = os.path.normpath(os.path.join(root, file))
            
            if ignore_manager.is_ignored(filepath):
                continue
            
            if filepath not in tracked_files:
                untracked_files.append(filepath)
    
    # Display status
    if short:
        # Short format (similar to git status -s)
        for file in staged_changes:
            if file in unstaged_changes:
                print(f"MM {file}")
            else:
                print(f"M  {file}")
        
        for file in unstaged_changes:
            if file not in staged_changes:
                print(f" M {file}")
        
        for file in deleted_files:
            print(f" D {file}")
        
        for file in untracked_files[:20]:  # Limit output
            print(f"?? {file}")
        
        if len(untracked_files) > 20:
            print(f"... and {len(untracked_files) - 20} more untracked files")
    
    else:
        # Long format (detailed)
        print(f"{Colors.BOLD}=== Repository Status ==={Colors.RESET}\n")
        
        # Branch info
        if current_branch:
            print(f"On branch {Colors.CYAN}{current_branch}{Colors.RESET}")
        else:
            print(f"HEAD detached at {Colors.YELLOW}{head_commit[:8] if head_commit else 'unknown'}{Colors.RESET}")
        
        if not head_commit:
            print("\nNo commits yet\n")
        
        # Staged changes
        if staged_changes:
            print(f"\n{Colors.GREEN}Changes to be committed:{Colors.RESET}")
            print(f"  (use 'wannabegit unstage <file>' to unstage)\n")
            for file in staged_changes:
                status_marker = "modified:" if file in tracked_files else "new file:"
                print(f"  {Colors.GREEN}{status_marker:12}{Colors.RESET} {file}")
        
        # Unstaged changes
        if unstaged_changes or deleted_files:
            print(f"\n{Colors.RED}Changes not staged for commit:{Colors.RESET}")
            print(f"  (use 'wannabegit add <file>' to stage)\n")
            for file in unstaged_changes:
                if file not in staged_changes:
                    print(f"  {Colors.RED}modified:{Colors.RESET:12} {file}")
            for file in deleted_files:
                print(f"  {Colors.RED}deleted:{Colors.RESET:12} {file}")
        
        # Untracked files
        if untracked_files:
            print(f"\n{Colors.RED}Untracked files:{Colors.RESET}")
            print(f"  (use 'wannabegit add <file>' to track)\n")
            for file in untracked_files[:20]:
                print(f"  {file}")
            if len(untracked_files) > 20:
                print(f"  ... and {len(untracked_files) - 20} more")
        
        # Clean status
        if not staged_changes and not unstaged_changes and not untracked_files and not deleted_files:
            print(f"\n{Colors.GREEN}Nothing to commit, working tree clean{Colors.RESET}")
        elif not staged_changes and not unstaged_changes and not deleted_files:
            print(f"\nnothing added to commit but untracked files present")
        
        print()
    
    return 0