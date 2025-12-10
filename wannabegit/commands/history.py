import os
from wannabegit.utils import ensure_vcs_exists, COMMITS_DIR, read_json

def cmd_history():
    ensure_vcs_exists()

    commits = sorted(os.listdir(COMMITS_DIR), reverse=True)

    for commit_id in commits:
        meta_path = os.path.join(COMMITS_DIR, commit_id, "meta.json")
        if not os.path.exists(meta_path):
            continue
        meta = read_json(meta_path, {})
        print(f"commit {meta['id']}")
        print(f"Date: {meta['timestamp']}")
        print(f"    {meta['message']}\n")
