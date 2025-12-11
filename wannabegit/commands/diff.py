"""
Enhanced diff command with multiple comparison modes
"""
import os
from wannabegit.core import Repository, COMMITS_DIR, INDEX_FILE, read_json
from wannabegit.diff_engine import generate_diff, get_diff_stats, Colors


def cmd_diff(commit1: str = None, commit2: str = None, cached: bool = False) -> int:
    """
    Show differences between commits, working directory, or staging area
    
    Args:
        commit1: First commit (or None for working directory)
        commit2: Second commit (or None for HEAD)
        cached: Show staged changes vs HEAD
    
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
    
    # Handle different diff modes
    if cached:
        # Diff between staging area and HEAD
        return diff_cached(head_commit)
    
    elif commit1 and commit2:
        # Diff between two commits
        return diff_commits(commit1, commit2)
    
    elif commit1:
        # Diff between commit and working directory
        return diff_commit_working(commit1)
    
    else:
        # Diff between HEAD and working directory
        if not head_commit:
            print("No commits yet. Nothing to diff.")
            return 0
        return diff_commit_working(head_commit)


def diff_commits(commit1: str, commit2: str) -> int:
    """Show diff between two commits"""
    c1_path = os.path.join(COMMITS_DIR, commit1)
    c2_path = os.path.join(COMMITS_DIR, commit2)
    
    if not os.path.exists(c1_path):
        print(f"Error: Commit '{commit1}' does not exist")
        return 1
    
    if not os.path.exists(c2_path):
        print(f"Error: Commit '{commit2}' does not exist")
        return 1
    
    # Get file lists
    c1_meta = read_json(os.path.join(c1_path, "meta.json"), {})
    c2_meta = read_json(os.path.join(c2_path, "meta.json"), {})
    
    c1_files = set(c1_meta.get("files", []))
    c2_files = set(c2_meta.get("files", []))
    
    all_files = c1_files | c2_files
    
    if not all_files:
        print("No files to compare")
        return 0
    
    print(f"{Colors.BOLD}Comparing {commit1[:8]} → {commit2[:8]}{Colors.RESET}\n")
    
    total_added = 0
    total_removed = 0
    files_changed = 0
    
    for file in sorted(all_files):
        c1_file = os.path.join(c1_path, file)
        c2_file = os.path.join(c2_path, file)
        
        # Handle file additions/deletions
        if not os.path.exists(c1_file):
            print(f"{Colors.GREEN}+++ New file: {file}{Colors.RESET}")
            if os.path.exists(c2_file):
                with open(c2_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    print(f"    {Colors.GREEN}+{lines} lines{Colors.RESET}\n")
                    total_added += lines
            files_changed += 1
            continue
        
        if not os.path.exists(c2_file):
            print(f"{Colors.RED}--- Deleted file: {file}{Colors.RESET}")
            with open(c1_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
                print(f"    {Colors.RED}-{lines} lines{Colors.RESET}\n")
                total_removed += lines
            files_changed += 1
            continue
        
        # Compare file contents
        try:
            with open(c1_file, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(c2_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            if old_content != new_content:
                print(f"{Colors.BOLD}diff --wannabegit a/{file} b/{file}{Colors.RESET}")
                diff = generate_diff(old_content, new_content, file)
                
                if diff:
                    print(diff)
                    added, removed, _ = get_diff_stats(old_content, new_content)
                    total_added += added
                    total_removed += removed
                    files_changed += 1
                else:
                    print("  (Binary files differ)")
                    files_changed += 1
                
                print()
        
        except UnicodeDecodeError:
            print(f"{Colors.YELLOW}Binary files {file} differ{Colors.RESET}\n")
            files_changed += 1
    
    # Summary
    if files_changed > 0:
        print(f"{Colors.BOLD}Summary:{Colors.RESET}")
        print(f"  {files_changed} file(s) changed")
        print(f"  {Colors.GREEN}+{total_added}{Colors.RESET} insertions")
        print(f"  {Colors.RED}-{total_removed}{Colors.RESET} deletions")
    else:
        print("No differences found")
    
    return 0


def diff_commit_working(commit_id: str) -> int:
    """Show diff between commit and working directory"""
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    
    if not os.path.exists(commit_path):
        print(f"Error: Commit '{commit_id}' does not exist")
        return 1
    
    meta = read_json(os.path.join(commit_path, "meta.json"), {})
    tracked_files = meta.get("files", [])
    
    if not tracked_files:
        print("No tracked files")
        return 0
    
    print(f"{Colors.BOLD}Changes in working directory since {commit_id[:8]}{Colors.RESET}\n")
    
    has_changes = False
    
    for file in sorted(tracked_files):
        committed_file = os.path.join(commit_path, file)
        working_file = file
        
        if not os.path.exists(working_file):
            print(f"{Colors.RED}--- Deleted: {file}{Colors.RESET}\n")
            has_changes = True
            continue
        
        try:
            with open(committed_file, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(working_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            if old_content != new_content:
                print(f"{Colors.BOLD}diff --wannabegit a/{file} b/{file}{Colors.RESET}")
                diff = generate_diff(old_content, new_content, file)
                print(diff)
                print()
                has_changes = True
        
        except UnicodeDecodeError:
            print(f"{Colors.YELLOW}Binary file {file} modified{Colors.RESET}\n")
            has_changes = True
    
    if not has_changes:
        print("No changes in working directory")
    
    return 0


def diff_cached(head_commit: str) -> int:
    """Show diff between staging area and HEAD"""
    if not head_commit:
        print("No HEAD commit. Showing all staged files:")
        return show_staged_files()
    
    index = read_json(INDEX_FILE, {"staged_files": {}})
    staged = index.get("staged_files", {})
    
    if not staged:
        print("No staged changes")
        return 0
    
    commit_path = os.path.join(COMMITS_DIR, head_commit)
    print(f"{Colors.BOLD}Staged changes (to be committed){Colors.RESET}\n")
    
    for file in sorted(staged.keys()):
        committed_file = os.path.join(commit_path, file)
        working_file = file
        
        if not os.path.exists(committed_file):
            print(f"{Colors.GREEN}+++ New file: {file}{Colors.RESET}\n")
            continue
        
        if not os.path.exists(working_file):
            print(f"{Colors.RED}--- Deleted: {file}{Colors.RESET}\n")
            continue
        
        try:
            with open(committed_file, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(working_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            if old_content != new_content:
                print(f"{Colors.BOLD}diff --wannabegit a/{file} b/{file}{Colors.RESET}")
                diff = generate_diff(old_content, new_content, file)
                print(diff)
                print()
        
        except UnicodeDecodeError:
            print(f"{Colors.YELLOW}Binary file {file} staged{Colors.RESET}\n")
    
    return 0


def show_staged_files() -> int:
    """Show list of staged files"""
    index = read_json(INDEX_FILE, {"staged_files": {}})
    staged = index.get("staged_files", {})
    
    for file in sorted(staged.keys()):
        print(f"  {Colors.GREEN}new file:{Colors.RESET} {file}")
    
    return 0