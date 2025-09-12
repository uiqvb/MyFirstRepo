import argparse
from tabulate import tabulate
import library
from typing import List, Dict


def cmd_list(sort: str = "id") -> None:
    """List all books in a formatted table."""
    books: List[Dict] = library.list_books()
    if not books:
        print("📚 No books in the library.")
        return

    # Optional sorting
    if sort == "title":
        books = sorted(books, key=lambda b: b["title"].lower())
    else:
        books = sorted(books, key=lambda b: b["id"])

    rows = [[b["id"], b["title"], b["author"], " Yes" if b["available"] else " No"] for b in books]
    print(tabulate(rows, headers=["ID", "Title", "Author", "Available"], tablefmt="github"))


def cmd_add(title: str, author: str) -> None:
    """Add a new book to the library."""
    try:
        new_id = library.add_book(title, author)
        print(f" Added book #{new_id}: '{title}' by {author}")
    except Exception as e:
        print(f" Failed to add book: {e}")


def cmd_toggle(book_id: int) -> None:
    """Toggle a book's availability by ID."""
    try:
        b = library.toggle_availability(book_id)
        status = " Yes" if b["available"] else " No"
        print(f" Toggled availability for book #{b['id']} → {status}")
    except KeyError:
        print(f" No book found with ID {book_id}.")
    except Exception as e:
        print(f"Error: {e}")


def cmd_search(query: str) -> None:
    """Search for books by title or author."""
    books: List[Dict] = library.list_books()
    results = [
        b for b in books
        if query.lower() in b["title"].lower() or query.lower() in b["author"].lower()
    ]

    if not results:
        print(f"🔍 No results found for '{query}'.")
        return

    rows = [[b["id"], b["title"], b["author"], "Yes" if b["available"] else "No"] for b in results]
    print(tabulate(rows, headers=["ID", "Title", "Author", "Available"], tablefmt="github"))


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Simple Library Management CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # list command
    p_list = sub.add_parser("list", help="List all books")
    p_list.add_argument("--sort", choices=["id", "title"], default="id", help="Sort books by ID or title")

    # add command
    p_add = sub.add_parser("add", help="Add a new book")
    p_add.add_argument("--title", required=True, help="Book title")
    p_add.add_argument("--author", required=True, help="Book author")

    # toggle command
    p_toggle = sub.add_parser("toggle", help="Toggle book availability")
    p_toggle.add_argument("--id", required=True, type=int, help="Book ID")

    # search command
    p_search = sub.add_parser("search", help="Search for books by title or author")
    p_search.add_argument("--query", required=True, help="Search term")

    args = parser.parse_args()

    if args.cmd == "list":
        cmd_list(args.sort)
    elif args.cmd == "add":
        cmd_add(args.title, args.author)
    elif args.cmd == "toggle":
        cmd_toggle(args.id)
    elif args.cmd == "search":
        cmd_search(args.query)


if __name__ == "__main__":
    main()
