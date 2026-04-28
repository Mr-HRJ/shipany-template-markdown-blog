r"""Fix anchor-in-anchor hydration errors in fumadocs TOC.

When a heading contains a markdown link or a bare URL, fumadocs renders the
TOC entry as an `<a href="#anchor">` wrapping the heading text. If the text
already contains an inner `<a>` (from `[text](url)` or GFM auto-link of a
bare URL), the result is `<a><a></a></a>` → invalid HTML, hydration error.

Two transforms, only inside heading lines (`^#{1,6}\s+...`):

  1. `[text](url)`            → `text`
  2. bare `https?://...`      → `` `https?://...` `` (inline code; GFM no
                                 longer auto-links code).

Scans content/docs/**/*.{md,mdx}.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "content" / "docs"

HEADING_RE = re.compile(r"^(#{1,6}\s+)(.+?)\s*$")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(https?://[^)\s]+(?:\s+\"[^\"]*\")?\)")
# bare URL not already inside backticks; we apply this AFTER stripping md
# links. Excludes whitespace, ASCII punctuation that ends URLs, and common CJK
# punctuation (U+3000 range, fullwidth comma U+FF0C) so a trailing 。/，/、
# isn't swallowed into the inline-code span.
BARE_URL_RE = re.compile(
    r"(?<!`)(https?://[^\s`)\]，。、！？…：；》」』]+)"
)


def fix_heading_text(text: str) -> str:
    text = MD_LINK_RE.sub(lambda m: m.group(1), text)
    text = BARE_URL_RE.sub(lambda m: f"`{m.group(1)}`", text)
    return text


def process(path: Path) -> int:
    src = path.read_text(encoding="utf-8")
    changed = 0
    out_lines: list[str] = []
    in_fence = False
    for line in src.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        m = HEADING_RE.match(line)
        if not m:
            out_lines.append(line)
            continue
        prefix, body = m.group(1), m.group(2)
        new_body = fix_heading_text(body)
        if new_body != body:
            changed += 1
            out_lines.append(f"{prefix}{new_body}")
        else:
            out_lines.append(line)
    if changed:
        path.write_text("\n".join(out_lines), encoding="utf-8")
    return changed


def main() -> None:
    total_files = 0
    total_lines = 0
    for ext in ("*.md", "*.mdx"):
        for f in DOCS.rglob(ext):
            n = process(f)
            if n:
                total_files += 1
                total_lines += n
                print(f"  [{n}] {f.relative_to(REPO)}")
    print(f"\nfixed {total_lines} heading(s) across {total_files} file(s)")


if __name__ == "__main__":
    main()
