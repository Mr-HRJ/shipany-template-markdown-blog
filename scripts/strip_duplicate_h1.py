"""Remove body H1 if it equals the frontmatter title (or fumadocs will render
two identical titles on the page, one from DocsTitle and one from MDX).

Idempotent: skips files that no longer have a duplicate.
"""

from __future__ import annotations
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ROOTS = ["joyflix", "nanobanana", "gamiary", "blog", "markdown-blog"]

# Frontmatter pattern: ---\ntitle: '...'\n---\n\n<body>
# yaml_quote doubles single quotes inside the title, so we un-escape '' -> '.
FM_RE = re.compile(r"^---\ntitle:\s*'((?:''|[^'])*)'\n---\n(.*)$", re.DOTALL)


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def strip_duplicate(path: pathlib.Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    m = FM_RE.match(raw)
    if not m:
        return False
    quoted_title, body = m.group(1), m.group(2)
    title = quoted_title.replace("''", "'")

    # Drop leading blank lines.
    stripped = body.lstrip("\n")
    lines = stripped.split("\n")
    if not lines:
        return False

    first = lines[0].strip()
    if not first.startswith("# "):
        return False
    first_text = first[2:].strip()
    if normalize(first_text) != normalize(title):
        return False

    # Remove the H1 line (plus one trailing blank line, if any).
    del lines[0]
    while lines and not lines[0].strip():
        del lines[0]
        break

    new_body = "\n".join(lines)
    new_text = f"---\ntitle: '{quoted_title}'\n---\n\n{new_body}"
    if not new_text.endswith("\n"):
        new_text += "\n"
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    count = 0
    for root in ROOTS:
        for mdx in (REPO / "content/docs" / root).rglob("*.mdx"):
            if strip_duplicate(mdx):
                print(f"stripped  {mdx.relative_to(REPO)}")
                count += 1
    print(f"\nstripped H1 from {count} file(s)")


if __name__ == "__main__":
    main()
