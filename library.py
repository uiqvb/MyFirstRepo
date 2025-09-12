import json
from pathlib import Path

DATA_PATH = Path(__file__).with_name("data.json")

def load_books():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_books(books):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2)

def list_books():
    return load_books()

def add_book(title, author):
    books = load_books()
    new_id = max((b["id"] for b in books), default=0) + 1
    books.append({"id": new_id, "title": title, "author": author, "available": True})
    save_books(books)
    return new_id

def toggle_availability(book_id):
    books = load_books()
    for b in books:
        if b["id"] == book_id:
            b["available"] = not b["available"]
            save_books(books)
            return b
    raise ValueError(f"Book id {book_id} not found")
