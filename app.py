#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from tabulate import tabulate
import library


def cmd_list(only: str | None = None) -> int:
    books = library.list_books()
    if only in {"yes", "no"}:
        want = (only == "yes")
        books = [b for b in books if bool(b.get("available")) == want]

    if not books:
        print("No books found.")
        return 0

    rows = [
        [b["id"], b["title"], b["author"], "Yes" if b.get("available") else "No"]
        for b in books
    ]
    print(tabulate(rows, headers=["ID", "Title", "Author", "Available"], tablefmt="github"))
    return 0


def cmd_add(title: str, author: str) -> int:
    try:
        new_id = library.add_book(title.strip(), author.strip())
    except Exception as e:
        print(f"Error adding book: {e}", file=sys.stderr)
        return 1
    print(f"Added book #{new_id}: {title} by {author}")
    return 0


def cmd_toggle(book_id: int) -> int:
    try:
        b = library.toggle_availability(book_id)
    except KeyError:
        print(f"Book #{book_id} not found.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error toggling book #{book_id}: {e}", file=sys.stderr)
        return 1
    print(f"Toggled availability for #{b['id']} → {'Yes' if b.get('available') else 'No'}")
    return 0


def cmd_delete(book_id: int) -> int:
    try:
        removed = library.delete_book(book_id)
    except KeyError:
        print(f"Book #{book_id} not found.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error deleting book #{book_id}: {e}", file=sys.stderr)
        return 1
    print(f"Deleted book #{book_id}: {removed.get('title', '(unknown)')} by {removed.get('author', '')}")
    return 0


def cmd_search(q: str) -> int:
    ql = q.lower()
    matches = [
        b for b in library.list_books()
        if ql in b["title"].lower() or ql in b["author"].lower()
    ]
    if not matches:
        print("No matches.")
        return 0

    rows = [
        [b["id"], b["title"], b["author"], "Yes" if b.get("available") else "No"]
        for b in matches
    ]
    print(tabulate(rows, headers=["ID", "Title", "Author", "Available"], tablefmt="github"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Library App")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List books")
    p_list.add_argument("--available", choices=["yes", "no"], help="Filter by availability")

    p_add = sub.add_parser("add", help="Add a new book")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--author", required=True)

    p_toggle = sub.add_parser("toggle", help="Toggle availability")
    p_toggle.add_argument("--id", required=True, type=int)

    p_delete = sub.add_parser("delete", help="Delete a book")
    p_delete.add_argument("--id", required=True, type=int)

    p_search = sub.add_parser("search", help="Search by title or author")
    p_search.add_argument("query", help="Search text")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "list":
        return cmd_list(getattr(args, "available", None))
    if args.cmd == "add":
        return cmd_add(args.title, args.author)
    if args.cmd == "toggle":
        return cmd_toggle(args.id)
    if args.cmd == "delete":
        return cmd_delete(args.id)
    if args.cmd == "search":
        return cmd_search(args.query)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
