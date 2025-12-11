"""
Enhanced file staging with pattern matching and recursive directory support
"""
import os
import glob
from pathlib import Path
from typing import List
from wannabegit.core import (
    Repository, INDEX_FILE, read_json, write_json, get_file_hash
)
from wannabegit.ignore import IgnoreManager


def expand_file_patterns(patterns: List[str]) -> List[str]:
    """Expand file patterns including wildcards and directories"""
    files = []
    
    for pattern in patterns:
        if os.path.isdir(pattern):
            # Add all files in directory recursively
            for root, _, filenames in os.walk(pattern):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        elif '*' in pattern or '?' in pattern:
            # Expand glob pattern
            files.extend(glob.glob(pattern, recursive=True))
        elif os.path.isfile(pattern):
            files.append(pattern)
        else:
            # File doesn't exist yet, might be created
            files.append(pattern)
    
    return files


def cmd_add(file_path: str, add_all: bool = False) -> int:
    """
    Add files to staging area
    
    Args:
        file_path: File path or pattern to add
        add_all: If True, add all modified tracked files
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    ignore_manager = IgnoreManager()
    index = read_json(INDEX_FILE, {
        "tracked_files": [],
        "staged_files": {},
        "version": "1.0"
    })
    
    # Ensure staged_files exists
    if "staged_files" not in index:
        index["staged_files"] = {}
    
    files_to_add = []
    
    if add_all:
        # Add all modified tracked files
        for tracked_file in index["tracked_files"]:
            if os.path.exists(tracked_file):
                files_to_add.append(tracked_file)
    else:
        # Expand patterns
        files_to_add = expand_file_patterns([file_path])
    
    added_count = 0
    ignored_count = 0
    error_count = 0
    
    for file in files_to_add:
        # Normalize path
        file = os.path.normpath(file)
        
        # Check if ignored
        if ignore_manager.is_ignored(file):
            ignored_count += 1
            continue
        
        # Check if file exists
        if not os.path.exists(file):
            print(f"Error: '{file}' does not exist")
            error_count += 1
            continue
        
        # Skip directories
        if os.path.isdir(file):
            continue
        
        # Add to tracking list if not already there
        if file not in index["tracked_files"]:
            index["tracked_files"].append(file)
        
        # Stage the file with its current hash
        try:
            file_hash = get_file_hash(file)
            index["staged_files"][file] = {
                "hash": file_hash,
                "status": "added" if file not in index["tracked_files"] else "modified"
            }
            added_count += 1
        except IOError as e:
            print(f"Error reading '{file}': {e}")
            error_count += 1
            continue
    
    # Save updated index
    try:
        write_json(INDEX_FILE, index)
    except Exception as e:
        print(f"Error saving index: {e}")
        return 1
    
    # Report results
    if added_count > 0:
        print(f"Added {added_count} file(s) to staging area")
    
    if ignored_count > 0:
        print(f"Ignored {ignored_count} file(s)")
    
    if error_count > 0:
        print(f"Failed to add {error_count} file(s)")
        return 1
    
    if added_count == 0 and ignored_count == 0:
        print("No files added")
    
    return 0


def cmd_unstage(file_path: str) -> int:
    """Remove file from staging area (keep tracking)"""
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    index = read_json(INDEX_FILE, {
        "tracked_files": [],
        "staged_files": {}
    })
    
    if file_path in index.get("staged_files", {}):
        del index["staged_files"][file_path]
        write_json(INDEX_FILE, index)
        print(f"Unstaged '{file_path}'")
        return 0
    else:
        print(f"File '{file_path}' is not staged")
        return 1