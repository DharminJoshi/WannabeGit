import difflib

def generate_diff(old_text, new_text):
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    return "".join(difflib.unified_diff(old_lines, new_lines, fromfile="old", tofile="new"))
