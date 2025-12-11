"""
Complete branch management with create, list, and delete operations
"""
import os
from wannabegit.core import Repository
from wannabegit.diff_engine import Colors


def cmd_branch(name: str) -> int:
    """
    Create a new branch
    
    Args:
        name: Branch name to create
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Validate branch name
    if not name or '/' in name or ' ' in name:
        print(f"Error: Invalid branch name '{name}'")
        print("Branch names cannot contain spaces or slashes")
        return 1
    
    # Check if branch already exists
    if repo.branch_exists(name):
        print(f"Error: Branch '{name}' already exists")
        return 1
    
    # Get current HEAD
    head_commit = repo.get_head()
    
    if not head_commit:
        print("Error: Cannot create branch - no commits yet")
        print("Make at least one commit first")
        return 1
    
    # Create branch reference
    branch_file = repo.refs_dir / name
    
    try:
        branch_file.write_text(f"{head_commit}\n")
        print(f"Created branch '{Colors.GREEN}{name}{Colors.RESET}' at {head_commit[:8]}")
        return 0
    
    except IOError as e:
        print(f"Error creating branch: {e}")
        return 1


def cmd_branch_list() -> int:
    """List all branches with current branch highlighted"""
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    branches = repo.list_branches()
    current_branch = repo.get_current_branch()
    
    if not branches:
        print("No branches yet")
        if not current_branch:
            print("Create a branch with: wannabegit branch <name>")
        return 0
    
    print(f"{Colors.BOLD}Branches:{Colors.RESET}")
    
    for branch in sorted(branches):
        if branch == current_branch:
            print(f"{Colors.GREEN}* {branch}{Colors.RESET} (current)")
        else:
            print(f"  {branch}")
    
    # Show detached HEAD warning
    if not current_branch:
        head = repo.get_head()
        print(f"\n{Colors.YELLOW}Currently in detached HEAD state at {head[:8] if head else 'unknown'}{Colors.RESET}")
    
    return 0


def cmd_branch_delete(name: str) -> int:
    """
    Delete a branch
    
    Args:
        name: Branch name to delete
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Check if branch exists
    if not repo.branch_exists(name):
        print(f"Error: Branch '{name}' does not exist")
        return 1
    
    # Prevent deleting current branch
    current_branch = repo.get_current_branch()
    if name == current_branch:
        print(f"Error: Cannot delete current branch '{name}'")
        print(f"Switch to another branch first: wannabegit checkout <branch>")
        return 1
    
    # Delete branch file
    branch_file = repo.refs_dir / name
    
    try:
        branch_file.unlink()
        print(f"Deleted branch '{Colors.RED}{name}{Colors.RESET}'")
        return 0
    
    except OSError as e:
        print(f"Error deleting branch: {e}")
        return 1


def cmd_branch_rename(old_name: str, new_name: str) -> int:
    """
    Rename a branch
    
    Args:
        old_name: Current branch name
        new_name: New branch name
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Validate names
    if not repo.branch_exists(old_name):
        print(f"Error: Branch '{old_name}' does not exist")
        return 1
    
    if repo.branch_exists(new_name):
        print(f"Error: Branch '{new_name}' already exists")
        return 1
    
    # Rename branch
    old_file = repo.refs_dir / old_name
    new_file = repo.refs_dir / new_name
    
    try:
        old_file.rename(new_file)
        
        # Update HEAD if this was the current branch
        current_branch = repo.get_current_branch()
        if current_branch == old_name:
            head_file = repo.vcs_dir / "HEAD"
            head_file.write_text(f"ref: refs/heads/{new_name}\n")
        
        print(f"Renamed branch '{old_name}' to '{new_name}'")
        return 0
    
    except OSError as e:
        print(f"Error renaming branch: {e}")
        return 1