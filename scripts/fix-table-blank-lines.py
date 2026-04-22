"""Collapse blank lines between consecutive markdown table rows.

GFM requires header / separator / data rows to be consecutive. The imported
docs have a blank line between every row, which breaks table parsing.

Usage:
    python scripts/fix-table-blank-lines.py [--dry-run] [paths...]

If no paths given, scans content/docs recursively for .md and .mdx files.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "content" / "docs"

# A table-ish row: starts with optional whitespace, then `|`, contains at
# least one more `|`, and ends with `|` (optionally followed by whitespace).
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")


def fix_text(text: str) -> tuple[str, int]:
    """Return (new_text, num_blank_lines_removed)."""
    # Preserve original line endings by splitting on \n and rejoining.
    lines = text.split("\n")
    out: list[str] = []
    removed = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Look for: table row, then one-or-more blank lines, then another table row.
        if TABLE_ROW.match(line):
            out.append(line)
            # Peek ahead: collapse blanks between this and the next table row.
            j = i + 1
            while j < n and lines[j].strip() == "":
                # We only collapse if a table row follows; so scan past blanks.
                k = j
                while k < n and lines[k].strip() == "":
                    k += 1
                if k < n and TABLE_ROW.match(lines[k]):
                    # Drop all blank lines in [j, k), jump to k.
                    removed += k - j
                    j = k
                else:
                    break
            i = j
            continue
        out.append(line)
        i += 1
    return "\n".join(out), removed


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(p.rglob("*.md"))
            files.extend(p.rglob("*.mdx"))
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()

    roots = [Path(p).resolve() for p in args.paths] if args.paths else [DEFAULT_DIR]
    files = iter_files(roots)

    changed = 0
    total_removed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        new, removed = fix_text(original)
        if new != original:
            changed += 1
            total_removed += removed
            try:
                shown = f.relative_to(ROOT)
            except ValueError:
                shown = f
            print(f"{'[dry] ' if args.dry_run else ''}{shown}: -{removed} blank lines")
            if not args.dry_run:
                f.write_text(new, encoding="utf-8")

    print(f"\nTouched {changed} files, removed {total_removed} blank lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
