"""
Enhanced history/log command with multiple display formats
"""
import os
from wannabegit.core import Repository, COMMITS_DIR, read_json
from wannabegit.diff_engine import Colors


def cmd_history(limit: int = None, oneline: bool = False) -> int:
    """
    Display commit history
    
    Args:
        limit: Maximum number of commits to show
        oneline: Show condensed one-line format
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Get HEAD commit
    head_commit = repo.get_head()
    current_branch = repo.get_current_branch()
    
    if not head_commit:
        print("No commits yet")
        return 0
    
    # Build commit chain
    commits = []
    current = head_commit
    visited = set()
    
    while current and current not in visited:
        visited.add(current)
        meta_path = os.path.join(COMMITS_DIR, current, "meta.json")
        
        if not os.path.exists(meta_path):
            break
        
        metadata = read_json(meta_path, {})
        if metadata:
            commits.append(metadata)
        
        current = metadata.get("parent")
        
        # Apply limit
        if limit and len(commits) >= limit:
            break
    
    if not commits:
        print("No commits found")
        return 0
    
    # Display commits
    if oneline:
        # One-line format
        for meta in commits:
            commit_id = meta.get("id", "unknown")[:8]
            message = meta.get("message", "No message")
            
            # Highlight HEAD
            if meta.get("id") == head_commit:
                branch_info = f"({Colors.CYAN}{current_branch or 'HEAD'}{Colors.RESET})"
                print(f"{Colors.YELLOW}{commit_id}{Colors.RESET} {branch_info} {message}")
            else:
                print(f"{Colors.YELLOW}{commit_id}{Colors.RESET} {message}")
    
    else:
        # Full format
        for i, meta in enumerate(commits):
            commit_id = meta.get("id", "unknown")
            message = meta.get("message", "No message")
            timestamp = meta.get("timestamp", "Unknown time")
            author = meta.get("author", {})
            author_name = author.get("name", "Unknown")
            author_email = author.get("email", "")
            files = meta.get("files", [])
            parent = meta.get("parent")
            
            # Highlight HEAD commit
            if meta.get("id") == head_commit:
                head_marker = f" {Colors.YELLOW}(HEAD -> {current_branch or 'detached'}){Colors.RESET}"
            else:
                head_marker = ""
            
            print(f"{Colors.YELLOW}commit {commit_id}{Colors.RESET}{head_marker}")
            
            if parent:
                print(f"Parent: {parent[:8]}")
            
            print(f"Author: {author_name} <{author_email}>")
            print(f"Date:   {timestamp}")
            print(f"\n    {message}")
            
            if files:
                print(f"\n    {len(files)} file(s) changed")
            
            # Add separator between commits
            if i < len(commits) - 1:
                print()
    
    return 0


def cmd_show(commit_id: str = None) -> int:
    """
    Show detailed information about a commit
    
    Args:
        commit_id: Commit to show (default: HEAD)
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Default to HEAD
    if not commit_id:
        commit_id = repo.get_head()
        if not commit_id:
            print("No commits yet")
            return 1
    
    # Load metadata
    meta_path = os.path.join(COMMITS_DIR, commit_id, "meta.json")
    
    if not os.path.exists(meta_path):
        print(f"Commit '{commit_id}' not found")
        return 1
    
    metadata = read_json(meta_path, {})
    
    # Display detailed info
    print(f"{Colors.YELLOW}commit {metadata.get('id')}{Colors.RESET}")
    
    parent = metadata.get("parent")
    if parent:
        print(f"Parent: {parent}")
    
    author = metadata.get("author", {})
    print(f"Author: {author.get('name', 'Unknown')} <{author.get('email', '')}>")
    print(f"Date:   {metadata.get('timestamp', 'Unknown')}")
    print(f"Branch: {metadata.get('branch', 'unknown')}")
    
    print(f"\n    {metadata.get('message', 'No message')}\n")
    
    files = metadata.get("files", [])
    if files:
        print(f"Files changed ({len(files)}):")
        for file in files:
            print(f"  {file}")
    
    return 0