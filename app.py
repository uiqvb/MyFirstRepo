import argparse
from tabulate import tabulate
import library

def cmd_list():
    rows = []
    for b in library.list_books():
        rows.append([b["id"], b["title"], b["author"], "Yes" if b["available"] else "No"])
    print(tabulate(rows, headers=["ID", "Title", "Author", "Available"], tablefmt="github"))

def cmd_add(title, author):
    new_id = library.add_book(title, author)
    print(f"Added book #{new_id}: {title} by {author}")

def cmd_toggle(book_id):
    b = library.toggle_availability(book_id)
    print(f"Toggled availability for #{b['id']} → {'Yes' if b['available'] else 'No'}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Library App")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all books")

    p_add = sub.add_parser("add", help="Add a new book")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--author", required=True)

    p_toggle = sub.add_parser("toggle", help="Toggle availability")
    p_toggle.add_argument("--id", required=True, type=int)

    args = p.parse_args()

    if args.cmd == "list":
        cmd_list()
    elif args.cmd == "add":
        cmd_add(args.title, args.author)
    elif args.cmd == "toggle":
        cmd_toggle(args.id)
