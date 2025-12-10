import os
import shutil
from datetime import datetime
from wannabegit.utils import (
    ensure_vcs_exists,
    COMMITS_DIR,
    INDEX_FILE,
    read_json,
    write_json,
    generate_commit_id,
    write_head
)

def cmd_commit(message):
    ensure_vcs_exists()

    index = read_json(INDEX_FILE, {"tracked_files": []})
    files = index["tracked_files"]

    if not files:
        print("No tracked files. Use `wannabegit add <file>` first.")
        return

    commit_id = generate_commit_id(message)
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    os.makedirs(commit_path)

    # Copy tracked files
    for f in files:
        if os.path.exists(f):
            shutil.copy(f, os.path.join(commit_path, os.path.basename(f)))

    metadata = {
        "id": commit_id,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": files
    }
    write_json(os.path.join(commit_path, "meta.json"), metadata)
    write_head(commit_id)

    print(f"Committed as {commit_id}")
