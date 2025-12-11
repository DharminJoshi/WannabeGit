"""
Enhanced commit command with parent tracking and better metadata
"""
import os
import shutil
from datetime import datetime
from wannabegit.core import (
    Repository, COMMITS_DIR, INDEX_FILE, read_json, write_json,
    generate_commit_id, format_timestamp, get_file_hash
)


def cmd_commit(message: str, commit_all: bool = False) -> int:
    """
    Create a new commit from staged files
    
    Args:
        message: Commit message
        commit_all: If True, stage and commit all tracked files
    
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
    
    # If commit_all, stage all tracked files
    if commit_all:
        for tracked_file in index["tracked_files"]:
            if os.path.exists(tracked_file):
                file_hash = get_file_hash(tracked_file)
                index["staged_files"][tracked_file] = {
                    "hash": file_hash,
                    "status": "modified"
                }
    
    staged_files = index.get("staged_files", {})
    
    if not staged_files:
        print("Nothing to commit (staging area is empty)")
        print("Use 'wannabegit add <file>' to stage files")
        return 1
    
    # Get parent commit
    parent_commit = repo.get_head()
    current_branch = repo.get_current_branch()
    
    # Generate commit ID
    timestamp = format_timestamp()
    commit_id = generate_commit_id(message, timestamp, parent_commit)
    
    # Create commit directory
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    
    try:
        os.makedirs(commit_path, exist_ok=True)
        
        # Copy staged files to commit
        files_committed = []
        for file_path in staged_files.keys():
            if os.path.exists(file_path):
                # Preserve directory structure
                rel_path = os.path.relpath(file_path)
                dest_path = os.path.join(commit_path, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
                files_committed.append(rel_path)
        
        # Get config for author info
        config = repo.get_config()
        user_name = config.get("user", {}).get("name", "Unknown")
        user_email = config.get("user", {}).get("email", "unknown@localhost")
        
        # Create commit metadata
        metadata = {
            "id": commit_id,
            "message": message,
            "timestamp": timestamp,
            "author": {
                "name": user_name,
                "email": user_email
            },
            "parent": parent_commit,
            "branch": current_branch or "detached",
            "files": files_committed,
            "stats": {
                "files_changed": len(files_committed),
                "total_files": len(files_committed)
            }
        }
        
        # Save metadata
        write_json(os.path.join(commit_path, "meta.json"), metadata)
        
        # Update HEAD
        repo.set_head(commit_id, current_branch)
        
        # Clear staging area but keep tracked files
        index["staged_files"] = {}
        write_json(INDEX_FILE, index)
        
        # Print success message
        branch_info = f"[{current_branch}]" if current_branch else "[detached HEAD]"
        print(f"{branch_info} {commit_id}: {message}")
        print(f"{len(files_committed)} file(s) changed")
        
        if len(files_committed) > 0:
            print("\nCommitted files:")
            for file in files_committed[:10]:  # Show first 10
                print(f"  {file}")
            if len(files_committed) > 10:
                print(f"  ... and {len(files_committed) - 10} more")
        
        return 0
        
    except (OSError, IOError) as e:
        print(f"Error creating commit: {e}")
        # Cleanup on failure
        if os.path.exists(commit_path):
            shutil.rmtree(commit_path)
        return 1


def get_commit_metadata(commit_id: str) -> dict:
    """Load commit metadata from commit ID"""
    meta_path = os.path.join(COMMITS_DIR, commit_id, "meta.json")
    return read_json(meta_path, {})


def get_commit_tree(commit_id: str) -> list:
    """Get list of commits from commit to root"""
    tree = []
    current = commit_id
    
    visited = set()  # Prevent infinite loops
    
    while current and current not in visited:
        visited.add(current)
        metadata = get_commit_metadata(current)
        
        if not metadata:
            break
        
        tree.append(metadata)
        current = metadata.get("parent")
    
    return tree