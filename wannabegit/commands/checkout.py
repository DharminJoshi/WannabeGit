import os
from wannabegit.utils import VCS_DIR, HEAD_FILE, COMMITS_DIR

def cmd_checkout(branch):
    branch_file = os.path.join(VCS_DIR, "refs", "heads", branch)

    if not os.path.exists(branch_file):
        print(f"Branch '{branch}' does not exist.")
        return

    with open(branch_file) as f:
        commit = f.read().strip()

    # Switch HEAD
    with open(HEAD_FILE, "w") as f:
        f.write(commit)

    print(f"Switched to branch '{branch}'.")
