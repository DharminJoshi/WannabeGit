import os
import json
import hashlib
from datetime import datetime

VCS_DIR = ".wannabegit"
COMMITS_DIR = os.path.join(VCS_DIR, "commits")
INDEX_FILE = os.path.join(VCS_DIR, "index.json")
HEAD_FILE = os.path.join(VCS_DIR, "HEAD")
REFS_DIR = os.path.join(VCS_DIR, "refs", "heads")


def ensure_vcs_exists():
    if not os.path.exists(VCS_DIR):
        print("Error: Repository not initialized. Run: wannabegit init")
        exit(1)


def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def generate_commit_id(message):
    h = hashlib.sha1()
    h.update((message + str(datetime.now())).encode("utf-8"))
    return h.hexdigest()[:6]


def write_head(commit_id):
    with open(HEAD_FILE, "w") as f:
        f.write(commit_id)
