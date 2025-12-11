#!/usr/bin/env python3
"""
WannabeGit - A lightweight CLI-based version control system
"""
import sys
import argparse
from wannabegit.commands.init import cmd_init
from wannabegit.commands.add import cmd_add
from wannabegit.commands.commit import cmd_commit
from wannabegit.commands.history import cmd_history
from wannabegit.commands.revert import cmd_revert
from wannabegit.commands.diff import cmd_diff
from wannabegit.commands.status import cmd_status
from wannabegit.commands.graph import cmd_graph
from wannabegit.commands.branch import cmd_branch
from wannabegit.commands.checkout import cmd_checkout


def create_parser():
    """Create and configure argument parser with subcommands"""
    parser = argparse.ArgumentParser(
        prog='wannabegit',
        description='A lightweight version control system',
        epilog='For more information on a command, use: wannabegit <command> --help'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init command
    subparsers.add_parser('init', help='Initialize a new repository')
    
    # add command
    add_parser = subparsers.add_parser('add', help='Add files to staging area')
    add_parser.add_argument('files', nargs='+', help='Files to add')
    add_parser.add_argument('-A', '--all', action='store_true', help='Add all modified files')
    
    # commit command
    commit_parser = subparsers.add_parser('commit', help='Create a new commit')
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')
    commit_parser.add_argument('-a', '--all', action='store_true', help='Commit all tracked files')
    
    # history/log command
    log_parser = subparsers.add_parser('history', aliases=['log'], help='Show commit history')
    log_parser.add_argument('-n', '--number', type=int, help='Limit number of commits shown')
    log_parser.add_argument('--oneline', action='store_true', help='Show condensed output')
    log_parser.add_argument('--graph', action='store_true', help='Show graph visualization')
    
    # revert command
    revert_parser = subparsers.add_parser('revert', help='Revert to a specific commit')
    revert_parser.add_argument('commit_id', help='Commit ID to revert to')
    revert_parser.add_argument('--hard', action='store_true', help='Discard all changes')
    
    # diff command
    diff_parser = subparsers.add_parser('diff', help='Show differences between commits')
    diff_parser.add_argument('commit1', nargs='?', help='First commit (default: working directory)')
    diff_parser.add_argument('commit2', nargs='?', help='Second commit (default: HEAD)')
    diff_parser.add_argument('--cached', action='store_true', help='Show staged changes')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show working tree status')
    status_parser.add_argument('-s', '--short', action='store_true', help='Show short format')
    
    # branch command
    branch_parser = subparsers.add_parser('branch', help='List, create, or delete branches')
    branch_parser.add_argument('name', nargs='?', help='Branch name to create')
    branch_parser.add_argument('-d', '--delete', help='Delete specified branch')
    branch_parser.add_argument('-l', '--list', action='store_true', help='List all branches')
    
    # checkout command
    checkout_parser = subparsers.add_parser('checkout', help='Switch branches or restore files')
    checkout_parser.add_argument('target', help='Branch name or commit ID')
    checkout_parser.add_argument('-b', '--create', action='store_true', help='Create new branch')
    
    return parser


def main():
    """Main entry point for WannabeGit CLI"""
    parser = create_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    try:
        # Route to appropriate command handler
        if args.command == 'init':
            return cmd_init()
        
        elif args.command == 'add':
            if args.all:
                return cmd_add('.', add_all=True)
            else:
                for file in args.files:
                    cmd_add(file)
                return 0
        
        elif args.command == 'commit':
            return cmd_commit(args.message, commit_all=args.all)
        
        elif args.command in ['history', 'log']:
            if args.graph:
                return cmd_graph(limit=args.number)
            else:
                return cmd_history(limit=args.number, oneline=args.oneline)
        
        elif args.command == 'revert':
            return cmd_revert(args.commit_id, hard=args.hard)
        
        elif args.command == 'diff':
            return cmd_diff(args.commit1, args.commit2, cached=args.cached)
        
        elif args.command == 'status':
            return cmd_status(short=args.short)
        
        elif args.command == 'branch':
            if args.delete:
                from wannabegit.commands.branch import cmd_branch_delete
                return cmd_branch_delete(args.delete)
            elif args.name:
                return cmd_branch(args.name)
            else:
                from wannabegit.commands.branch import cmd_branch_list
                return cmd_branch_list()
        
        elif args.command == 'checkout':
            return cmd_checkout(args.target, create_branch=args.create)
        
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())