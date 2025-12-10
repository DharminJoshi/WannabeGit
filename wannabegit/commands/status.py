import os
from wannabegit.utils import INDEX_FILE, read_json, COMMITS_DIR, HEAD_FILE
from wannabegit.ignore import is_ignored

def cmd_status():
    tracked = read_json(INDEX_FILE, {"tracked_files": []})["tracked_files"]

    # HEAD commit
    head = open(HEAD_FILE).read().strip()
    head_path = os.path.join(COMMITS_DIR, head) if head else None

    print("=== STATUS ===")

    # Modified
    if head_path and os.path.exists(head_path):
        print("\nModified files:")
        for f in tracked:
            working = open(f).read()
            committed = open(os.path.join(head_path, os.path.basename(f))).read()
            if working != committed:
                print("    M", f)
    else:
        print("No commits yet.")

    # Untracked
    print("\nUntracked files:")
    for f in os.listdir("."):
        if os.path.isfile(f) and f not in tracked and not is_ignored(f):
            print("    ?", f)

    # Ignored
    print("\nIgnored files:")
    for f in os.listdir("."):
        if is_ignored(f):
            print("    I", f)

    print("\nTracked:")
    for f in tracked:
        print("    ", f)
