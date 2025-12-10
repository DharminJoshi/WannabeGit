import os
from wannabegit.utils import VCS_DIR, COMMITS_DIR, INDEX_FILE, HEAD_FILE, write_json

def cmd_init():
    if os.path.exists(VCS_DIR):
        print("Repository already exists.")
        return

    os.makedirs(COMMITS_DIR)
    os.makedirs(os.path.join(VCS_DIR, "refs", "heads"))
    write_json(INDEX_FILE, {"tracked_files": []})

    with open(HEAD_FILE, "w") as f:
        f.write("")

    print("Initialized empty wannabegit repository.")
