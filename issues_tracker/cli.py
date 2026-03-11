"""Command-line interface for the issue tracker."""
import argparse
import sys

from .tracker import IssueTracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="issues",
        description="Simple issue tracker CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # create
    create_p = subparsers.add_parser("create", help="Create a new issue")
    create_p.add_argument("title", help="Issue title")
    create_p.add_argument("-d", "--description", default="", help="Issue description")
    create_p.add_argument("--storage", default="issues.json", help="Path to storage file")

    # list
    list_p = subparsers.add_parser("list", help="List all issues")
    list_p.add_argument("--status", choices=["open", "closed"], help="Filter by status")
    list_p.add_argument("--storage", default="issues.json", help="Path to storage file")

    # close
    close_p = subparsers.add_parser("close", help="Close an issue")
    close_p.add_argument("id", help="Issue ID (or prefix)")
    close_p.add_argument("--storage", default="issues.json", help="Path to storage file")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    tracker = IssueTracker(storage_path=args.storage)

    if args.command == "create":
        issue = tracker.create_issue(title=args.title, description=args.description)
        print(f"Created issue: {issue}")
        return 0

    if args.command == "list":
        issues = tracker.list_issues(status=args.status)
        if not issues:
            print("No issues found.")
        for issue in issues:
            print(issue)
        return 0

    if args.command == "close":
        issue = tracker.close_issue(args.id)
        if issue:
            print(f"Closed issue: {issue}")
        else:
            print(f"Issue '{args.id}' not found.", file=sys.stderr)
            return 1
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
