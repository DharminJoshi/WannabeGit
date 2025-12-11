"""
Enhanced checkout command with safety checks and file restoration
"""
import os
import shutil
from wannabegit.core import Repository, COMMITS_DIR, read_json, INDEX_FILE
from wannabegit.diff_engine import Colors


def has_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes in working directory"""
    repo = Repository()
    head_commit = repo.get_head()
    
    if not head_commit:
        return False
    
    index = read_json(INDEX_FILE, {"tracked_files": []})
    tracked = index.get("tracked_files", [])
    
    commit_path = os.path.join(COMMITS_DIR, head_commit)
    
    for file in tracked:
        if not os.path.exists(file):
            return True
        
        committed_file = os.path.join(commit_path, file)
        if not os.path.exists(committed_file):
            continue
        
        try:
            with open(file, 'rb') as f:
                working = f.read()
            with open(committed_file, 'rb') as f:
                committed = f.read()
            
            if working != committed:
                return True
        except IOError:
            continue
    
    return False


def restore_files_from_commit(commit_id: str, force: bool = False) -> bool:
    """Restore files from a commit to working directory"""
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    
    if not os.path.exists(commit_path):
        return False
    
    meta = read_json(os.path.join(commit_path, "meta.json"), {})
    files = meta.get("files", [])
    
    for file in files:
        src = os.path.join(commit_path, file)
        dst = file
        
        if not os.path.exists(src):
            continue
        
        try:
            # Create parent directories if needed
            os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
            shutil.copy2(src, dst)
        except IOError as e:
            print(f"Warning: Could not restore '{file}': {e}")
    
    return True


def cmd_checkout(target: str, create_branch: bool = False, force: bool = False) -> int:
    """
    Switch branches or restore files
    
    Args:
        target: Branch name or commit ID
        create_branch: Create new branch if it doesn't exist
        force: Force checkout even with uncommitted changes
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    current_branch = repo.get_current_branch()
    
    # Check for uncommitted changes
    if not force and has_uncommitted_changes():
        print(f"{Colors.RED}Error: You have uncommitted changes{Colors.RESET}")
        print("Please commit or stash them before switching branches")
        print("Or use --force to discard changes")
        return 1
    
    # Handle branch creation
    if create_branch:
        # Create new branch at current HEAD
        head_commit = repo.get_head()
        
        if not head_commit:
            print("Error: Cannot create branch - no commits yet")
            return 1
        
        if repo.branch_exists(target):
            print(f"Error: Branch '{target}' already exists")
            return 1
        
        # Create branch
        branch_file = repo.refs_dir / target
        branch_file.write_text(f"{head_commit}\n")
        print(f"Created new branch '{Colors.GREEN}{target}{Colors.RESET}'")
    
    # Check if target is a branch
    if repo.branch_exists(target):
        # Switching to existing branch
        branch_file = repo.refs_dir / target
        commit_id = branch_file.read_text().strip()
        
        if not commit_id:
            print(f"Error: Branch '{target}' has no commits")
            return 1
        
        # Restore files from branch's commit
        if not restore_files_from_commit(commit_id, force):
            print(f"Error: Could not restore files from branch '{target}'")
            return 1
        
        # Update HEAD to point to branch
        repo.set_head(commit_id, target)
        
        # Update index with tracked files from commit
        meta = read_json(os.path.join(COMMITS_DIR, commit_id, "meta.json"), {})
        index = read_json(INDEX_FILE, {"tracked_files": [], "staged_files": {}})
        index["tracked_files"] = meta.get("files", [])
        index["staged_files"] = {}  # Clear staging area
        
        from wannabegit.core import write_json
        write_json(INDEX_FILE, index)
        
        if current_branch:
            print(f"Switched from branch '{current_branch}' to '{Colors.CYAN}{target}{Colors.RESET}'")
        else:
            print(f"Switched to branch '{Colors.CYAN}{target}{Colors.RESET}'")
        
        return 0
    
    # Check if target is a commit ID
    commit_path = os.path.join(COMMITS_DIR, target)
    
    if os.path.exists(commit_path):
        # Detached HEAD checkout
        if not restore_files_from_commit(target, force):
            print(f"Error: Could not restore files from commit '{target}'")
            return 1
        
        # Set HEAD to commit (detached)
        repo.set_head(target)
        
        # Update index
        meta = read_json(os.path.join(commit_path, "meta.json"), {})
        index = read_json(INDEX_FILE, {"tracked_files": [], "staged_files": {}})
        index["tracked_files"] = meta.get("files", [])
        index["staged_files"] = {}
        
        from wannabegit.core import write_json
        write_json(INDEX_FILE, index)
        
        print(f"{Colors.YELLOW}Note: Switching to '{target[:8]}'.{Colors.RESET}")
        print(f"You are in 'detached HEAD' state.")
        print(f"If you want to create a new branch: wannabegit checkout -b <branch-name>")
        
        return 0
    
    # Target not found
    print(f"Error: Branch or commit '{target}' not found")
    
    # Suggest similar branches
    branches = repo.list_branches()
    similar = [b for b in branches if target.lower() in b.lower()]
    
    if similar:
        print(f"\nDid you mean:")
        for branch in similar:
            print(f"  {branch}")
    
    return 1


def cmd_checkout_file(file_path: str, commit_id: str = None) -> int:
    """
    Restore a specific file from a commit
    
    Args:
        file_path: File to restore
        commit_id: Commit to restore from (default: HEAD)
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    if not commit_id:
        commit_id = repo.get_head()
        if not commit_id:
            print("Error: No commits yet")
            return 1
    
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    
    if not os.path.exists(commit_path):
        print(f"Error: Commit '{commit_id}' not found")
        return 1
    
    src_file = os.path.join(commit_path, file_path)
    
    if not os.path.exists(src_file):
        print(f"Error: File '{file_path}' not found in commit '{commit_id[:8]}'")
        return 1
    
    try:
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        shutil.copy2(src_file, file_path)
        print(f"Restored '{file_path}' from {commit_id[:8]}")
        return 0
    
    except IOError as e:
        print(f"Error restoring file: {e}")
        return 1