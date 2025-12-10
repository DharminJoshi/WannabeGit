import os
from wannabegit.utils import COMMITS_DIR

def cmd_graph():
    commits = sorted(os.listdir(COMMITS_DIR))

    print("=== COMMIT GRAPH ===")
    for c in commits:
        print(f"* {c}")
