"""
Visual commit graph display with branch visualization
"""
import os
from typing import Dict, List, Set, Tuple
from wannabegit.core import Repository, COMMITS_DIR, read_json
from wannabegit.diff_engine import Colors


def build_commit_graph() -> Dict[str, dict]:
    """Build a graph of all commits with their relationships"""
    graph = {}
    
    if not os.path.exists(COMMITS_DIR):
        return graph
    
    for commit_id in os.listdir(COMMITS_DIR):
        commit_path = os.path.join(COMMITS_DIR, commit_id)
        
        if not os.path.isdir(commit_path):
            continue
        
        meta = read_json(os.path.join(commit_path, "meta.json"), {})
        
        if meta:
            graph[commit_id] = {
                "parent": meta.get("parent"),
                "message": meta.get("message", "No message"),
                "timestamp": meta.get("timestamp", "Unknown"),
                "author": meta.get("author", {}),
                "branch": meta.get("branch", ""),
                "children": []
            }
    
    # Build children relationships
    for commit_id, data in graph.items():
        parent = data["parent"]
        if parent and parent in graph:
            graph[parent]["children"].append(commit_id)
    
    return graph


def get_commit_chain(commit_id: str, graph: Dict[str, dict]) -> List[str]:
    """Get chain of commits from commit to root"""
    chain = []
    current = commit_id
    visited = set()
    
    while current and current in graph and current not in visited:
        visited.add(current)
        chain.append(current)
        current = graph[current]["parent"]
    
    return chain


def cmd_graph(limit: int = None) -> int:
    """
    Display visual commit graph
    
    Args:
        limit: Maximum number of commits to show
    
    Returns:
        0 on success, 1 on error
    """
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Build commit graph
    graph = build_commit_graph()
    
    if not graph:
        print("No commits yet")
        return 0
    
    # Get HEAD and current branch
    head_commit = repo.get_head()
    current_branch = repo.get_current_branch()
    
    # Get all branches
    branches = repo.list_branches()
    branch_heads = {}
    
    for branch in branches:
        branch_file = repo.refs_dir / branch
        if branch_file.exists():
            commit = branch_file.read_text().strip()
            if commit:
                if commit not in branch_heads:
                    branch_heads[commit] = []
                branch_heads[commit].append(branch)
    
    # Build commit chain from HEAD
    if head_commit and head_commit in graph:
        commits = get_commit_chain(head_commit, graph)
        
        if limit:
            commits = commits[:limit]
    else:
        # Show all commits sorted by timestamp
        commits = sorted(graph.keys(), 
                        key=lambda x: graph[x]["timestamp"], 
                        reverse=True)
        if limit:
            commits = commits[:limit]
    
    # Display graph
    print(f"{Colors.BOLD}=== COMMIT GRAPH ==={Colors.RESET}\n")
    
    for i, commit_id in enumerate(commits):
        data = graph[commit_id]
        
        # Build branch labels
        labels = []
        
        if commit_id == head_commit:
            if current_branch:
                labels.append(f"{Colors.CYAN}HEAD -> {current_branch}{Colors.RESET}")
            else:
                labels.append(f"{Colors.YELLOW}HEAD{Colors.RESET}")
        
        if commit_id in branch_heads:
            for branch in branch_heads[commit_id]:
                if branch != current_branch or commit_id != head_commit:
                    labels.append(f"{Colors.GREEN}{branch}{Colors.RESET}")
        
        label_str = f" ({', '.join(labels)})" if labels else ""
        
        # Graph line
        if i == 0:
            connector = "* "
        else:
            connector = "* "
        
        # Commit info
        short_id = commit_id[:8]
        message = data["message"]
        timestamp = data["timestamp"]
        author = data["author"].get("name", "Unknown")
        
        print(f"{Colors.YELLOW}{connector}{short_id}{Colors.RESET}{label_str}")
        print(f"  {message}")
        print(f"  {Colors.DIM}{author} • {timestamp}{Colors.RESET}")
        
        # Show parent connection
        if i < len(commits) - 1:
            print("  |")
    
    # Show statistics
    print(f"\n{Colors.BOLD}Statistics:{Colors.RESET}")
    print(f"  Total commits: {len(graph)}")
    print(f"  Branches: {len(branches)}")
    
    # Show orphaned commits (not reachable from any branch)
    reachable = set()
    for branch in branches:
        branch_file = repo.refs_dir / branch
        if branch_file.exists():
            commit = branch_file.read_text().strip()
            if commit:
                reachable.update(get_commit_chain(commit, graph))
    
    orphaned = set(graph.keys()) - reachable
    if orphaned:
        print(f"  {Colors.YELLOW}Orphaned commits: {len(orphaned)}{Colors.RESET}")
    
    return 0


def cmd_graph_ascii(limit: int = None) -> int:
    """Display ASCII art commit graph (alternative view)"""
    repo = Repository()
    
    try:
        repo.ensure_exists()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    graph = build_commit_graph()
    
    if not graph:
        print("No commits yet")
        return 0
    
    head_commit = repo.get_head()
    
    if not head_commit or head_commit not in graph:
        print("No HEAD commit")
        return 0
    
    commits = get_commit_chain(head_commit, graph)
    
    if limit:
        commits = commits[:limit]
    
    print("Commit Graph (Newest → Oldest)\n")
    print("=" * 60)
    
    for i, commit_id in enumerate(commits):
        data = graph[commit_id]
        
        # ASCII graph
        if i == 0:
            print("┌─ HEAD")
            print("│")
        
        short_id = commit_id[:8]
        message = data["message"][:50]
        
        print(f"├─● {short_id}: {message}")
        
        if i < len(commits) - 1:
            print("│")
        else:
            print("└─ (root)")
    
    print("=" * 60)
    
    return 0