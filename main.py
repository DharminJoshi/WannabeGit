#!/usr/bin/env python3
import sys
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


def main():
    if len(sys.argv) < 2:
        print("Usage: wannabegit <command> [args]")
        return

    cmd = sys.argv[1]

    if cmd == "init":
        cmd_init()

    elif cmd == "add" and len(sys.argv) == 3:
        cmd_add(sys.argv[2])

    elif cmd == "commit" and "-m" in sys.argv:
        msg_index = sys.argv.index("-m") + 1
        message = sys.argv[msg_index]
        cmd_commit(message)

    elif cmd == "history":
        cmd_history()

    elif cmd == "revert" and len(sys.argv) == 3:
        cmd_revert(sys.argv[2])

    elif cmd == "diff" and len(sys.argv) == 4:
        cmd_diff(sys.argv[2], sys.argv[3])

    elif cmd == "status":
        cmd_status()

    elif cmd == "log" and "--graph" in sys.argv:
        cmd_graph()

    elif cmd == "branch" and len(sys.argv) == 3:
        cmd_branch(sys.argv[2])

    elif cmd == "checkout" and len(sys.argv) == 3:
        cmd_checkout(sys.argv[2])

    else:
        print("Unknown or incomplete command.")


if __name__ == "__main__":
    main()
