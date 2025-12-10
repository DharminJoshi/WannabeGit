import os
from wannabegit.utils import COMMITS_DIR
from wannabegit.diff_engine import generate_diff

def cmd_diff(commit1, commit2):
    c1 = os.path.join(COMMITS_DIR, commit1)
    c2 = os.path.join(COMMITS_DIR, commit2)

    if not os.path.exists(c1) or not os.path.exists(c2):
        print("Error: One of the commits does not exist.")
        return

    files1 = os.listdir(c1)
    files2 = os.listdir(c2)

    print(f"Comparing {commit1} → {commit2}\n")

    for f in files1:
        if f == "meta.json":
            continue
        file1 = open(os.path.join(c1, f)).read()
        file2 = open(os.path.join(c2, f)).read()
        diff = generate_diff(file1, file2)
        print(f"--- {f} ---")
        print(diff if diff else "No changes.")
