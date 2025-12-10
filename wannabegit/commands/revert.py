import os
import shutil
from wannabegit.utils import ensure_vcs_exists, COMMITS_DIR, read_json, write_head

def cmd_revert(commit_id):
    ensure_vcs_exists()
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    if not os.path.exists(commit_path):
        print(f"Error: commit '{commit_id}' does not exist.")
        return

    meta = read_json(os.path.join(commit_path, "meta.json"), {})

    for f in meta["files"]:
        src = os.path.join(commit_path, os.path.basename(f))
        if os.path.exists(src):
            shutil.copy(src, f)

    write_head(commit_id)
    print(f"Reverted to commit {commit_id}.")
