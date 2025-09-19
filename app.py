import argparse
from tabulate import tabulate
import library
import sys
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def _bool_str(val: bool) -> str:
    return "Yes" if val else "No"

def _norm(s: str) -> str:
    return s.lower().strip()

def _exit(msg: str, code: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(code)

def _validate_field(name: str, allowed: List[str]):
    if name not in allowed:
        _exit(f"Invalid value '{name}'. Allowed: {', '.join(allowed)}")

def _load_all() -> List[Dict[str, Any]]:
    # Expect library.list_books() -> iterable of dicts with id,title,author,available
    return list(library.list_books())

# ---------- Commands ----------

def cmd_list(q: Optional[str], available: Optional[bool], sort: str, desc: bool,
             export: Optional[Path], out_format: Optional[str]):
    rows = _load_all()

    # filter by search
    if q:
        nq = _norm(q)
        rows = [b for b in rows if nq in _norm(b.get("title","")) or nq in _norm(b.get("author",""))]

    # filter by availability
    if available is not None:
        rows = [b for b in rows if bool(b.get("available")) == available]

    # sort
    _validate_field(sort, ["id", "title", "author", "available"])
    rows.sort(key=lambda b: (_norm(str(b.get(sort))) if isinstance(b.get(sort), str) else b.get(sort)), reverse=desc)

    # print table
    table = [[b["id"], b["title"], b["author"], _bool_str(bool(b["available"]))] for b in rows]
    print(tabulate(table, headers=["ID", "Title", "Author", "Available"], tablefmt="github"))
    print(f"\n{len(rows)} result(s).")

    # export if requested
    if export:
        if not out_format:
            # infer from extension
            ext = export.suffix.lower()
            out_format = "json" if ext == ".json" else "csv"
        out_format = out_format.lower()

        export.parent.mkdir(parents=True, exist_ok=True)
        if out_format == "json":
            with export.open("w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
        elif out_format == "csv":
            with export.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["id", "title", "author", "available"])
                w.writeheader()
                for r in rows:
                    w.writerow({"id": r.get("id"), "title": r.get("title"), "author": r.get("author"),
                                "available": bool(r.get("available"))})
        else:
            _exit(f"Unsupported export format: {out_format}. Use csv|json.")
        print(f"Exported {len(rows)} record(s) to {export}")

def cmd_add(title: str, author: str, available: Optional[bool]):
    new_id = library.add_book(title, author)  # keeping your existing API
    # If caller asked to set availability explicitly and it differs, toggle until it matches.
    if available is not None:
        # We don’t assume a set API; we derive by reading and possibly toggling.
        # Find the newly added book:
        added = next((b for b in _load_all() if b.get("id") == new_id), None)
        if added and bool(added.get("available")) != available:
            library.toggle_availability(new_id)
    print(f"Added book #{new_id}: {title} by {author}")

def cmd_toggle(ids: List[int]):
    if not ids:
        _exit("No IDs provided for toggle.")
    for bid in ids:
        try:
            b = library.toggle_availability(bid)
            print(f"Toggled availability for #{b['id']} → {_bool_str(bool(b['available']))}")
        except Exception as e:
            print(f"Failed to toggle #{bid}: {e}", file=sys.stderr)

def cmd_import(csv_path: Path, dry_run: bool):
    if not csv_path.exists():
        _exit(f"File not found: {csv_path}")
    added = 0
    with csv_path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        # Expect columns: title, author
        for i, row in enumerate(r, start=1):
            title = (row.get("title") or "").strip()
            author = (row.get("author") or "").strip()
            if not title or not author:
                print(f"Skipping line {i}: missing title/author", file=sys.stderr)
                continue
            if dry_run:
                print(f"[DRY-RUN] Would add: {title} by {author}")
            else:
                library.add_book(title, author)
                added += 1
    if dry_run:
        print("Dry-run complete.")
    else:
        print(f"Imported {added} book(s) from {csv_path}")

def cmd_stats():
    rows = _load_all()
    total = len(rows)
    avail = sum(1 for b in rows if bool(b.get("available")))
    unavail = total - avail
    data = [
        ["Total", total],
        ["Available", avail],
        ["Unavailable", unavail],
    ]
    print(tabulate(data, headers=["Metric", "Count"], tablefmt="github"))

# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(description="Library App")
    sub = p.add_subparsers(dest="cmd", required=True)

    # list
    p_list = sub.add_parser("list", help="List books (supports search/filter/sort/export)")
    p_list.add_argument("--q", help="Search by title/author (substring)")
    p_list.add_argument("--available", choices=["true", "false"], help="Filter by availability")
    p_list.add_argument("--sort", default="id", help="Sort by: id|title|author|available (default: id)")
    p_list.add_argument("--desc", action="store_true", help="Sort descending")
    p_list.add_argument("--export", type=Path, help="Export to file (csv or json; infers by extension)")
    p_list.add_argument("--format", choices=["csv", "json"], help="Force export format (overrides extension)")

    # add
    p_add = sub.add_parser("add", help="Add a new book")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--author", required=True)
    p_add.add_argument("--available", choices=["true", "false"],
                       help="Set initial availability (default = whatever the backend uses)")

    # toggle
    p_toggle = sub.add_parser("toggle", help="Toggle availability for one or more IDs")
    p_toggle.add_argument("--id", dest="ids", required=True, nargs="+", type=int)

    # import
    p_import = sub.add_parser("import", help="Bulk add from CSV with columns: title,author")
    p_import.add_argument("--file", type=Path, required=True)
    p_import.add_argument("--dry-run", action="store_true", help="Validate without adding")

    # stats
    sub.add_parser("stats", help="Show totals/availability counts")

    args = p.parse_args()

    if args.cmd == "list":
        avail = None
        if args.available is not None:
            avail = args.available.lower() == "true"
        cmd_list(q=args.q, available=avail, sort=args.sort, desc=args.desc,
                 export=args.export, out_format=args.format)

    elif args.cmd == "add":
        avail = None
        if args.available is not None:
            avail = args.available.lower() == "true"
        cmd_add(args.title, args.author, avail)

    elif args.cmd == "toggle":
        cmd_toggle(args.ids)

    elif args.cmd == "import":
        cmd_import(args.file, args.dry_run)

    elif args.cmd == "stats":
        cmd_stats()

if __name__ == "__main__":
    main()
