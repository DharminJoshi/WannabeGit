"""
Enhanced revert command with hard/soft options and safety checks
"""
import os
import shutil
from wannabegit.core import (
    Repository, COMMITS_DIR, INDEX_FILE, read_json, write_json
)
from wannabegit.diff_engine import Colors


def cmd_revert(commit_id: str, hard: bool = False) -> int:
    """
    Revert working directory to a specific commit
    
    Args:
        commit_id: Commit ID to revert to
        hard: If True, discard all changes. If False, keep working changes
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    
    if not os.path.exists(commit_path):
        print(f"Error: Commit '{commit_id}' does not exist")
        
        # Suggest similar commits
        all_commits = [d for d in os.listdir(COMMITS_DIR) if os.path.isdir(os.path.join(COMMITS_DIR, d))]
        similar = [c for c in all_commits if commit_id.lower() in c.lower()]
        
        if similar:
            print("\nDid you mean:")
            for c in similar[:5]:
                meta = read_json(os.path.join(COMMITS_DIR, c, "meta.json"), {})
                msg = meta.get("message", "No message")
                print(f"  {c[:8]}: {msg}")
        
        return 1
    
    # Load commit metadata
    meta = read_json(os.path.join(commit_path, "meta.json"), {})
    files = meta.get("files", [])
    commit_msg = meta.get("message", "No message")
    
    if not files:
        print(f"Warning: Commit '{commit_id}' has no files")
    
    # Check for uncommitted changes
    index = read_json(INDEX_FILE, {"tracked_files": [], "staged_files": {}})
    has_staged = len(index.get("staged_files", {})) > 0
    
    if has_staged and not hard:
        print(f"{Colors.YELLOW}Warning: You have staged changes{Colors.RESET}")
        print("Use --hard to discard them, or commit them first")
        
        response = input("Continue anyway? [y/N]: ").strip().lower()
        if response != 'y':
            print("Revert cancelled")
            return 0
    
    # Perform revert
    try:
        restored_count = 0
        error_count = 0
        
        for file in files:
            src = os.path.join(commit_path, file)
            dst = file
            
            if not os.path.exists(src):
                print(f"Warning: '{file}' not in commit, skipping")
                continue
            
            try:
                # Create parent directories
                os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
                shutil.copy2(src, dst)
                restored_count += 1
            except IOError as e:
                print(f"Error restoring '{file}': {e}")
                error_count += 1
        
        # Update HEAD
        current_branch = repo.get_current_branch()
        repo.set_head(commit_id, current_branch)
        
        # Update index
        if hard:
            # Clear staged changes
            index["staged_files"] = {}
        
        # Update tracked files
        index["tracked_files"] = files
        write_json(INDEX_FILE, index)
        
        # Report results
        print(f"\n{Colors.GREEN}Reverted to commit {commit_id[:8]}{Colors.RESET}")
        print(f"Message: {commit_msg}")
        print(f"Restored {restored_count} file(s)")
        
        if error_count > 0:
            print(f"{Colors.RED}Failed to restore {error_count} file(s){Colors.RESET}")
        
        if hard:
            print(f"\n{Colors.YELLOW}Hard revert performed - all changes discarded{Colors.RESET}")
        else:
            print(f"\nSoft revert - working directory changes preserved")
        
        return 0
        
    except Exception as e:
        print(f"Error during revert: {e}")
        return 1


def cmd_reset(mode: str = "mixed") -> int:
    """
    Reset current HEAD to specified state
    
    Args:
        mode: 'soft', 'mixed', or 'hard'
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    head_commit = repo.get_head()
    
    if not head_commit:
        print("No HEAD commit to reset")
        return 1
    
    index = read_json(INDEX_FILE, {"tracked_files": [], "staged_files": {}})
    
    if mode == "soft":
        # Keep both staged and working changes, just move HEAD
        print(f"Reset HEAD to {head_commit[:8]} (soft)")
        print("Staged changes and working directory preserved")
    
    elif mode == "mixed":
        # Keep working changes, clear staging area
        index["staged_files"] = {}
        write_json(INDEX_FILE, index)
        print(f"Reset HEAD to {head_commit[:8]} (mixed)")
        print("Staging area cleared, working directory preserved")
    
    elif mode == "hard":
        # Discard all changes
        commit_path = os.path.join(COMMITS_DIR, head_commit)
        meta = read_json(os.path.join(commit_path, "meta.json"), {})
        files = meta.get("files", [])
        
        # Restore all files
        for file in files:
            src = os.path.join(commit_path, file)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(file) or '.', exist_ok=True)
                shutil.copy2(src, file)
        
        # Clear staging
        index["staged_files"] = {}
        index["tracked_files"] = files
        write_json(INDEX_FILE, index)
        
        print(f"Reset HEAD to {head_commit[:8]} (hard)")
        print(f"{Colors.RED}All changes discarded{Colors.RESET}")
    
    else:
        print(f"Error: Unknown reset mode '{mode}'")
        print("Valid modes: soft, mixed, hard")
        return 1
    
    return 0