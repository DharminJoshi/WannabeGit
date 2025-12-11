"""
Repository initialization command with configuration setup
"""
import os
from wannabegit.core import (
    VCS_DIR, COMMITS_DIR, INDEX_FILE, HEAD_FILE, CONFIG_FILE,
    write_json, Repository
)
from wannabegit.ignore import create_default_ignore_file


def cmd_init() -> int:
    """
    Initialize a new WannabeGit repository
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    if repo.exists():
        print("Repository already initialized.")
        print(f"WannabeGit repository found in: {repo.vcs_dir}")
        return 0
    
    try:
        # Create directory structure
        os.makedirs(COMMITS_DIR, exist_ok=True)
        os.makedirs(os.path.join(VCS_DIR, "objects"), exist_ok=True)
        os.makedirs(os.path.join(VCS_DIR, "refs", "heads"), exist_ok=True)
        os.makedirs(os.path.join(VCS_DIR, "refs", "tags"), exist_ok=True)
        
        # Initialize index (staging area)
        write_json(INDEX_FILE, {
            "tracked_files": [],
            "staged_files": {},
            "version": "1.0"
        })
        
        # Initialize HEAD to point to main branch
        with open(HEAD_FILE, "w", encoding="utf-8") as f:
            f.write("ref: refs/heads/main\n")
        
        # Create main branch reference (empty for now)
        main_ref = os.path.join(VCS_DIR, "refs", "heads", "main")
        with open(main_ref, "w", encoding="utf-8") as f:
            f.write("")
        
        # Initialize config
        config = {
            "core": {
                "repositoryformatversion": 0,
                "filemode": True,
                "bare": False
            },
            "user": {
                "name": os.environ.get("USER", "Unknown User"),
                "email": f"{os.environ.get('USER', 'user')}@localhost"
            }
        }
        write_json(CONFIG_FILE, config)
        
        # Create default .wannabegitignore
        create_default_ignore_file()
        
        print("Initialized empty WannabeGit repository")
        print(f"Repository path: {os.path.abspath(VCS_DIR)}")
        print(f"Default branch: main")
        print(f"\nNext steps:")
        print(f"  1. Add files: wannabegit add <file>")
        print(f"  2. Commit: wannabegit commit -m 'Initial commit'")
        
        return 0
        
    except OSError as e:
        print(f"Error initializing repository: {e}")
        return 1