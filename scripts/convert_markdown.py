"""Import raw markdown from 出海全链路手册Markdown版本/*/*.md into content/docs/{slug}/*.md.

Each source file becomes {slug}.md with YAML frontmatter (title = original stem).
Also writes a root meta.json with category ordering and per-category meta.json
for page ordering (curated, from scripts/page_order.py).

Run:
    python scripts/convert_markdown.py
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page_order import PAGE_ORDER  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
SRC = Path("C:/Users/VULCAN/Desktop/出海全链路手册Markdown版本")
DOCS = REPO / "content" / "docs"

# Source (Chinese) -> slug, display title. Order here = root meta.json order.
CATEGORIES = [
    ("网站出海必读", "must-read", "网站出海必读"),
    ("找需求", "ideas", "找需求"),
    ("数据分析", "analytics", "数据分析"),
    ("开发", "dev", "开发"),
    ("支付", "payment", "支付"),
    ("Seo", "seo", "SEO"),
    ("GEO", "geo", "GEO 优化"),
    ("外链", "backlink", "外链"),
    ("流量", "traffic", "流量"),
    ("Ads", "ads", "Ads 投流"),
    ("其他", "misc", "其他"),
    ("复盘", "review", "复盘"),
]


def file_slug(name: str, max_len: int = 18) -> str:
    """Allowlist slug: a-zA-Z0-9 + CJK Unified Ideographs + dashes only.
    Truncate to max_len so URL-encoded Windows paths stay under MAX_PATH (260)."""
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9一-鿿-]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).strip("-")
    if len(stem) > max_len:
        stem = stem[:max_len].rstrip("-")
    return stem or "untitled"


def _unique_slug(cat_slug: str, slug: str, seen: dict) -> str:
    key = (cat_slug, slug)
    n = seen.get(key, 0) + 1
    seen[key] = n
    return slug if n == 1 else f"{slug}-{n}"


# ---------- Title normalization for curated-order matching ----------

_SMART_PUNCT = {
    "“": "", "”": "", "‘": "", "’": "",
    "「": "", "」": "", "『": "", "』": "",
    "'": "", '"': "",
    "，": ",", "。": ".", "：": ":", "；": ";",
    "（": "(", "）": ")", "【": "[", "】": "]",
    "？": "?", "！": "!", "、": ",",
    "／": "/", "　": " ",
    "→": "->", "–": "-", "—": "-",
    "%": "%",
}


def norm_title(s: str) -> str:
    """Loose-match key: strip whitespace, normalize smart punctuation, lowercase ASCII.
    Drop `/ , . : ; ( ) [ ] ? ! space` so tiny punctuation shifts don't miss matches."""
    for k, v in _SMART_PUNCT.items():
        s = s.replace(k, v)
    s = s.lower()
    # Drop punctuation/spaces that often vary between source filename and reference title
    s = re.sub(r"[\s\-_./,:;()\[\]?!#&+]+", "", s)
    return s


# ---------- Content transforms ----------

_REMOTE_IMG_RE = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)(?:\s+\"[^\"]*\")?\)")
_LANG_REWRITE = {"dot": "text", "graphviz": "text"}
_FENCE_RE = re.compile(r"^(\s*```|\s*~~~)([A-Za-z0-9_+\-]*)(.*)$")
# Match a full tag: <name attrs>  (attrs may end with / for self-close)
_FULL_TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b([^<>]*?)(/?)>")
_VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def rewrite_remote_images(body: str) -> str:
    """Convert remote `![alt](https://...)` to HTML `<img>` so fumadocs'
    remarkImage plugin doesn't try to fetch size at build time."""
    def repl(m: re.Match) -> str:
        alt = m.group(1).replace('"', "&quot;")
        url = m.group(2)
        return f'<img src="{url}" alt="{alt}" />'
    return _REMOTE_IMG_RE.sub(repl, body)


def rewrite_fence_langs(body: str) -> str:
    """Rewrite code fences whose language isn't in the Shiki bundle."""
    out = []
    for line in body.split("\n"):
        m = _FENCE_RE.match(line)
        if m:
            prefix, lang, rest = m.group(1), m.group(2), m.group(3)
            if lang in _LANG_REWRITE:
                lang = _LANG_REWRITE[lang]
            out.append(f"{prefix}{lang}{rest}")
        else:
            out.append(line)
    return "\n".join(out)


def escape_prose_html(body: str) -> str:
    """Escape `<` only when the tag would break MDX:
      - Skip inside fenced code blocks and inline code spans.
      - Keep self-closing tags (`<foo ... />`).
      - Keep void-element open tags (`<img ...>`, `<br>`, etc.).
      - Keep tags that have a matching close on the same line (balanced pair).
      - Everything else (orphan open-tag like bare `<head>` mention) gets `\\<`.
    """
    out_lines: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        parts = line.split("`")
        for i in range(0, len(parts), 2):
            parts[i] = _escape_prose_segment(parts[i])
        out_lines.append("`".join(parts))
    return "\n".join(out_lines)


def _escape_prose_segment(seg: str) -> str:
    def repl(m: re.Match) -> str:
        is_close = bool(m.group(1))
        name = m.group(2)
        self_close = bool(m.group(4))
        name_lower = name.lower()
        if self_close:
            return m.group(0)
        if not is_close and name_lower in _VOID_ELEMENTS:
            return m.group(0)
        # Is this open tag balanced by a close tag later in the segment?
        if not is_close:
            close_re = re.compile(rf"</{re.escape(name)}\s*>", re.IGNORECASE)
            if close_re.search(seg, m.end()):
                return m.group(0)
        # Unbalanced — escape the leading <
        return "\\" + m.group(0)

    return _FULL_TAG_RE.sub(repl, seg)


# ---------- Page ordering ----------

def order_pages(cat_zh: str, stem_to_slug: dict[str, str]) -> list[str]:
    """Return slugs ordered to match PAGE_ORDER[cat_zh].
    Unmatched source files appended at the end in alphabetical stem order."""
    curated = PAGE_ORDER.get(cat_zh, [])
    norm_stems: dict[str, str] = {norm_title(stem): stem for stem in stem_to_slug}
    used: set[str] = set()
    ordered: list[str] = []
    for ref_title in curated:
        key = norm_title(ref_title)
        stem = norm_stems.get(key)
        if stem and stem not in used:
            ordered.append(stem_to_slug[stem])
            used.add(stem)
        else:
            print(f"  [warn] {cat_zh}: no source match for reference title: {ref_title!r}")
    leftovers = sorted(s for s in stem_to_slug if s not in used)
    for stem in leftovers:
        ordered.append(stem_to_slug[stem])
        print(f"  [info] {cat_zh}: appended unlisted source: {stem!r}")
    return ordered


# ---------- Main ----------

def main():
    if not SRC.exists():
        sys.exit(f"missing source: {SRC}")

    DOCS.mkdir(parents=True, exist_ok=True)

    (DOCS / "index.mdx").write_text(
        "---\ntitle: 'AI 出海手册'\n---\n\n"
        "AI 出海全链路知识库：找需求、开发、SEO、GEO、流量、投流、外链、数据分析、支付、复盘。\n",
        encoding="utf-8",
    )

    seen: dict = {}
    total = 0
    summary: list[tuple[str, str, int]] = []
    for cat_zh, cat_slug, cat_title in CATEGORIES:
        cat_dir = SRC / cat_zh
        if not cat_dir.exists():
            print(f"[skip] {cat_zh} not found")
            continue
        out_dir = DOCS / cat_slug
        out_dir.mkdir(parents=True, exist_ok=True)

        mds = sorted(cat_dir.glob("*.md"))
        stem_to_slug: dict[str, str] = {}
        for md in mds:
            stem = md.stem
            slug = _unique_slug(cat_slug, file_slug(md.name), seen)
            title = stem.replace("'", "''")
            body = md.read_text(encoding="utf-8")
            body = rewrite_remote_images(body)
            body = rewrite_fence_langs(body)
            body = escape_prose_html(body)
            out = out_dir / f"{slug}.mdx"
            out.write_text(f"---\ntitle: '{title}'\n---\n\n{body}".rstrip() + "\n", encoding="utf-8")
            stem_to_slug[stem] = slug
            total += 1

        pages = order_pages(cat_zh, stem_to_slug)
        (out_dir / "meta.json").write_text(
            json.dumps({"title": cat_title, "pages": pages}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary.append((cat_slug, cat_title, len(mds)))
        print(f"[{cat_slug}] {len(mds)} file(s)")

    (DOCS / "meta.json").write_text(
        json.dumps(
            {"title": "AI 出海手册", "pages": [slug for slug, _, _ in summary]},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"\n=== done: {total} files across {len(summary)} categories ===")


if __name__ == "__main__":
    main()
