#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from tabulate import tabulate
import library
import sys
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

    print(f"Added book #{new_id}: {title} by {author}")
    return 0



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

    p_delete = sub.add_parser("delete", help="Delete a book")
    p_delete.add_argument("--id", required=True, type=int)

    p_search = sub.add_parser("search", help="Search by title or author")
    p_search.add_argument("query", help="Search text")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "list":

