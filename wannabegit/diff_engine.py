"""
Advanced diff engine with color support and multiple diff formats
"""
import difflib
from typing import List, Tuple
from enum import Enum


class DiffFormat(Enum):
    """Supported diff output formats"""
    UNIFIED = "unified"
    CONTEXT = "context"
    NDIFF = "ndiff"
    SIDE_BY_SIDE = "side_by_side"


class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


def colorize_diff_line(line: str, use_color: bool = True) -> str:
    """Add color to diff line based on prefix"""
    if not use_color:
        return line
    
    if line.startswith('+') and not line.startswith('+++'):
        return f"{Colors.GREEN}{line}{Colors.RESET}"
    elif line.startswith('-') and not line.startswith('---'):
        return f"{Colors.RED}{line}{Colors.RESET}"
    elif line.startswith('@@'):
        return f"{Colors.CYAN}{line}{Colors.RESET}"
    elif line.startswith('+++') or line.startswith('---'):
        return f"{Colors.BOLD}{line}{Colors.RESET}"
    
    return line


def generate_diff(old_text: str, new_text: str, 
                 file_name: str = "file",
                 format_type: DiffFormat = DiffFormat.UNIFIED,
                 use_color: bool = True,
                 context_lines: int = 3) -> str:
    """
    Generate diff between two text strings with various format options
    
    Args:
        old_text: Original text content
        new_text: Modified text content
        file_name: Name of file for diff headers
        format_type: Output format (unified, context, etc.)
        use_color: Whether to add ANSI color codes
        context_lines: Number of context lines to show
    
    Returns:
        Formatted diff string
    """
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    
    # Add newlines if missing
    if old_lines and not old_lines[-1].endswith('\n'):
        old_lines[-1] += '\n'
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'
    
    if format_type == DiffFormat.UNIFIED:
        diff_lines = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{file_name}",
            tofile=f"b/{file_name}",
            n=context_lines
        )
        diff_text = "".join(diff_lines)
        
    elif format_type == DiffFormat.CONTEXT:
        diff_lines = difflib.context_diff(
            old_lines, new_lines,
            fromfile=f"a/{file_name}",
            tofile=f"b/{file_name}",
            n=context_lines
        )
        diff_text = "".join(diff_lines)
        
    elif format_type == DiffFormat.NDIFF:
        diff_lines = difflib.ndiff(old_lines, new_lines)
        diff_text = "".join(diff_lines)
        
    else:  # SIDE_BY_SIDE
        return generate_side_by_side_diff(old_lines, new_lines, file_name)
    
    # Apply color if requested
    if use_color and diff_text:
        lines = diff_text.split('\n')
        colored_lines = [colorize_diff_line(line, use_color) for line in lines]
        return '\n'.join(colored_lines)
    
    return diff_text


def generate_side_by_side_diff(old_lines: List[str], new_lines: List[str], 
                               file_name: str, width: int = 80) -> str:
    """Generate side-by-side diff view"""
    output = []
    output.append(f"{'=' * width}")
    output.append(f"{'OLD':^{width//2}} | {'NEW':^{width//2}}")
    output.append(f"{'=' * width}")
    
    max_len = max(len(old_lines), len(new_lines))
    
    for i in range(max_len):
        old_line = old_lines[i].rstrip() if i < len(old_lines) else ""
        new_line = new_lines[i].rstrip() if i < len(new_lines) else ""
        
        # Truncate if too long
        col_width = width // 2 - 2
        old_line = old_line[:col_width]
        new_line = new_line[:col_width]
        
        output.append(f"{old_line:<{col_width}} | {new_line:<{col_width}}")
    
    return '\n'.join(output)


def get_diff_stats(old_text: str, new_text: str) -> Tuple[int, int, int]:
    """
    Calculate diff statistics
    
    Returns:
        Tuple of (lines_added, lines_removed, lines_changed)
    """
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    diff = difflib.unified_diff(old_lines, new_lines, lineterm='')
    
    added = 0
    removed = 0
    
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            added += 1
        elif line.startswith('-') and not line.startswith('---'):
            removed += 1
    
    changed = min(added, removed)
    
    return added, removed, changed


def generate_word_diff(old_text: str, new_text: str) -> str:
    """Generate word-level diff for more granular comparison"""
    old_words = old_text.split()
    new_words = new_text.split()
    
    diff = difflib.unified_diff(old_words, new_words, lineterm='')
    return ' '.join(diff)


def is_binary_file(content: bytes) -> bool:
    """Check if content appears to be binary"""
    # Check for null bytes in first 8KB
    sample = content[:8192]
    return b'\x00' in sample


def generate_binary_diff_message(file_name: str) -> str:
    """Generate message for binary file diff"""
    return f"Binary files a/{file_name} and b/{file_name} differ\n"


def generate_summary_stats(old_text: str, new_text: str) -> str:
    """Generate summary statistics for diff"""
    added, removed, changed = get_diff_stats(old_text, new_text)
    
    return (
        f"{Colors.GREEN}+{added} insertions{Colors.RESET}, "
        f"{Colors.RED}-{removed} deletions{Colors.RESET}"
    )