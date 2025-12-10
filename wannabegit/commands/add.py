import os
from wannabegit.utils import ensure_vcs_exists, INDEX_FILE, read_json, write_json
from wannabegit.ignore import is_ignored

def cmd_add(file_path):
    ensure_vcs_exists()

    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' does not exist.")
        return

    if is_ignored(file_path):
        print(f"Ignored file: '{file_path}'")
        return

    index = read_json(INDEX_FILE, {"tracked_files": []})

    if file_path not in index["tracked_files"]:
        index["tracked_files"].append(file_path)

    write_json(INDEX_FILE, index)
    print(f"Added '{file_path}' to tracking index.")
