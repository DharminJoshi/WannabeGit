import os
from wannabegit.utils import VCS_DIR, HEAD_FILE

def cmd_branch(name):
    refs = os.path.join(VCS_DIR, "refs", "heads")
    os.makedirs(refs, exist_ok=True)

    head_commit = open(HEAD_FILE).read().strip()

    with open(os.path.join(refs, name), "w") as f:
        f.write(head_commit)

    print(f"Created branch '{name}'.")
