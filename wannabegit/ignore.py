import os
import fnmatch

IGNORE_FILE = ".wannabegitignore"

def load_ignore_patterns():
    if not os.path.exists(IGNORE_FILE):
        return []
    return [line.strip() for line in open(IGNORE_FILE) if line.strip()]

def is_ignored(filename):
    patterns = load_ignore_patterns()
    for p in patterns:
        if fnmatch.fnmatch(filename, p):
            return True
    return False
