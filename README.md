# WannabeGit - A Lightweight Version Control System

A Git-inspired CLI-based version control system built in Python with enhanced features and improved architecture.

## Features

### Core Version Control
- **Repository Management**: Initialize and manage local repositories
- **File Tracking**: Add files to staging area with pattern matching support
- **Commits**: Create commits with metadata, parent tracking, and branching
- **History**: View commit history with multiple display formats
- **Branches**: Create, list, delete, and switch between branches
- **Diff Engine**: Advanced file comparison with color-coded output
- **Status**: Comprehensive working directory status tracking

### Enhanced Features
- **Colored Terminal Output**: Beautiful, Git-like colored interface
- **Pattern Matching**: Add multiple files using wildcards (e.g., `*.py`)
- **Ignore Patterns**: Gitignore-style file exclusion
- **Detached HEAD**: Support for checking out specific commits
- **Safety Checks**: Prevent data loss with uncommitted change detection
- **Commit Graph**: Visual representation of commit history
- **Parent Tracking**: Full commit ancestry and history chain
- **Branch Management**: Complete branch operations with validation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd wannabegit

# Make the main script executable (optional)
chmod +x main.py

# Run directly
python main.py <command>

# Or create an alias
alias wannabegit='python /path/to/wannabegit/main.py'
```

## Quick Start

```bash
# Initialize a new repository
wannabegit init

# Add files to staging area
wannabegit add file.txt
wannabegit add *.py              # Add all Python files
wannabegit add -A                # Add all modified tracked files

# Create a commit
wannabegit commit -m "Initial commit"

# View status
wannabegit status
wannabegit status -s             # Short format

# View history
wannabegit history
wannabegit history --oneline     # Condensed format
wannabegit history -n 5          # Limit to 5 commits

# Create and switch branches
wannabegit branch feature-x      # Create branch
wannabegit branch -l             # List branches
wannabegit checkout feature-x    # Switch to branch
wannabegit checkout -b new-feat  # Create and switch

# View differences
wannabegit diff                  # Working dir vs HEAD
wannabegit diff --cached         # Staged vs HEAD
wannabegit diff abc123 def456    # Between commits

# Visualize commit graph
wannabegit history --graph
```

## Command Reference

### Repository Initialization
```bash
wannabegit init
```
Creates a new WannabeGit repository in the current directory.

### File Staging
```bash
# Add specific files
wannabegit add <file1> <file2> ...

# Add with wildcards
wannabegit add *.txt

# Add all modified tracked files
wannabegit add -A
```

### Committing Changes
```bash
# Create commit
wannabegit commit -m "Commit message"

# Commit all tracked files
wannabegit commit -m "Message" -a
```

### Viewing Status
```bash
# Detailed status
wannabegit status

# Short format
wannabegit status -s
```

### Viewing History
```bash
# Full history
wannabegit history

# Limited history
wannabegit history -n 10

# One-line format
wannabegit history --oneline

# Visual graph
wannabegit history --graph
```

### Branch Management
```bash
# List branches
wannabegit branch -l

# Create branch
wannabegit branch <branch-name>

# Delete branch
wannabegit branch -d <branch-name>

# Switch branches
wannabegit checkout <branch-name>

# Create and switch
wannabegit checkout -b <new-branch>
```

### Comparing Changes
```bash
# Compare working directory with HEAD
wannabegit diff

# Compare staged changes with HEAD
wannabegit diff --cached

# Compare two commits
wannabegit diff <commit1> <commit2>
```

### Reverting Changes
```bash
# Soft revert (keep working changes)
wannabegit revert <commit-id>

# Hard revert (discard all changes)
wannabegit revert <commit-id> --hard
```

## Repository Structure

```
.wannabegit/
├── commits/           # Commit storage
│   └── <commit-id>/
│       ├── meta.json  # Commit metadata
│       └── <files>    # Committed files
├── objects/           # Object storage (future use)
├── refs/
│   └── heads/         # Branch references
│       └── <branch>   # Branch pointer files
├── HEAD               # Current HEAD reference
├── index.json         # Staging area
└── config.json        # Repository configuration
```

## Configuration

The `.wannabegit/config.json` file stores repository settings:

```json
{
  "core": {
    "repositoryformatversion": 0,
    "filemode": true,
    "bare": false
  },
  "user": {
    "name": "Dharmin Joshi / DevKay",
    "email": "devkay@example.com"
  }
}
```

## Ignore Patterns

Create a `.wannabegitignore` file to exclude files:

```
# Python
*.pyc
__pycache__/
*.pyo

# Virtual environments
venv/
env/

# IDEs
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
```

Patterns follow gitignore syntax:
- `*.ext` - Matches all files with extension
- `dir/` - Matches entire directory
- `!file` - Negates previous pattern
- `/abs` - Absolute path from repo root

## Advanced Features

### Detached HEAD State
You can checkout specific commits directly:
```bash
wannabegit checkout abc123
```
This puts you in "detached HEAD" state where you're not on any branch.

### Commit Metadata
Each commit stores comprehensive metadata:
- Commit ID (8-character hash)
- Parent commit reference
- Author information
- Timestamp
- Branch context
- File listing

### Safety Features
- **Uncommitted Change Detection**: Prevents branch switching with uncommitted changes
- **Branch Validation**: Ensures branch names are valid
- **Parent Tracking**: Maintains commit history integrity
- **Force Options**: Override safety checks when needed

## Color Coding

Terminal output uses colors for clarity:
- **Green**: Additions, current branch, success
- **Red**: Deletions, errors, warnings
- **Yellow**: Modifications, HEAD marker, notes
- **Cyan**: Branch names, info
- **Bold**: Headers, important info

## Comparison with Git

### Similar Features
- Repository initialization
- File staging and commits
- Branch management
- Commit history
- Diff visualization
- Ignore patterns

### Key Differences
- Simpler commit ID generation (8 chars vs 40)
- No remote repository support
- No merge/rebase operations
- Simplified object storage
- Single-directory commits (no complex tree structures)

## Development

### Project Structure
```
wannabegit/
├── main.py                 # CLI entry point
├── wannabegit/
│   ├── __init__.py
│   ├── core.py            # Core repository logic
│   ├── diff_engine.py     # Diff generation
│   ├── ignore.py          # Ignore pattern matching
│   ├── utils.py           # Utility functions
│   └── commands/          # Command implementations
│       ├── add.py
│       ├── branch.py
│       ├── checkout.py
│       ├── commit.py
│       ├── diff.py
│       ├── graph.py
│       ├── history.py
│       ├── init.py
│       ├── revert.py
│       └── status.py
```

### Extending WannabeGit

To add new commands:
1. Create command module in `wannabegit/commands/`
2. Implement command function with signature: `def cmd_name(**kwargs) -> int`
3. Add parser configuration in `main.py`
4. Import and route in `main()` function

## Troubleshooting

### Repository Not Found
```
Error: Not a wannabegit repository
```
**Solution**: Run `wannabegit init` in your project directory

### Nothing to Commit
```
Nothing to commit (staging area is empty)
```
**Solution**: Add files with `wannabegit add <file>`

### Uncommitted Changes
```
Error: You have uncommitted changes
```
**Solution**: Either commit changes or use `--force` flag

### Branch Already Exists
```
Error: Branch 'name' already exists
```
**Solution**: Use a different name or delete the existing branch

## Future Enhancements

Potential features for future development:
- Remote repository support (push/pull)
- Merge and rebase operations
- Cherry-pick commits
- Stash functionality
- Tag support
- Submodule management
- Interactive staging
- Conflict resolution tools
- Performance optimizations
- Binary file handling improvements

## ⚖️ License

This project is licensed under the **CC BY-NC 4.0**  License.  
See the [LICENSE](LICENSE) file for full details.

---

## ⚠️ Disclaimer

This tool is intended **for educational and personal use only**.  
Accuracy of distance measurement depends on proper calibration and camera positioning.

> Provided "as is" — the developer (/'s) assumes no liability for any misuse or consequences.

---

## Contributing

Contributions are welcome! Areas for improvement:
- Additional commands
- Performance optimizations
- Better error handling
- Test coverage
- Documentation enhancements

## 📬 Contact

- **Developer:** Dharmin Joshi / DevKay  
- **Email:** info.dharmin@gmail.com  
- **LinkedIn:** [linkedin.com/in/dharmin-joshi-3bab42232](https://www.linkedin.com/in/dharmin-joshi-3bab42232/)  
- **GitHub:** [github.com/DharminJoshi](https://github.com/DharminJoshi)  

---

## Acknowledgments

Inspired by Git and built to understand version control internals.
