"""Generalized scraper for doc.16781678.xyz site sections.

Adapts fetch_shipany_docs.py to run over multiple sites in one pass:

    python scripts/fetch_doc_sites.py joyflix nanobanana gamiary blog markdown-blog

For each site:
  1. Harvest all `/<site>/<cat>/<slug>` URLs from the root page + one page per
     discovered category (covers any sidebar entries only revealed deeper in).
  2. Fetch each URL, extract the RSC-embedded markdown, auto-detect title from
     the first `#` heading (fallback: slug).
  3. Emit `content/docs/<site>/<cat>/<slug>.mdx` + per-folder `meta.json`.
  4. The `frequently-asked-questions` URL segment maps to local folder `faq`.

Outputs are idempotent — delete a site's folder before re-running to start
fresh.
"""

from __future__ import annotations
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

# Reuse the battle-tested extract / transform pipeline.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_shipany_docs import (  # noqa: E402
    extract_markdown,
    fetch_html,
    rewrite_remote_images,
    rewrite_fence_langs,
    fix_smart_quotes_in_tags,
    self_close_void_tags,
    wrap_bare_esm_lines,
    escape_prose_html,
    yaml_quote,
)

_SUBCATS = {"getting-started", "configuration", "payment", "deployment",
            "video-tutorials", "frequently-asked-questions", "others"}
_REL_LINK_RE = re.compile(r"\]\(/([a-z0-9\-]+)/([a-z0-9\-]+)(#[^)]*)?\)")


def rewrite_internal_links(body: str, site_slug: str) -> str:
    """Rewrite source-site relative links `/cat/page` → `/docs/<site>/<cat>/page`.

    Also maps the `frequently-asked-questions` URL segment to our local `faq`
    folder so links still resolve.
    """
    def repl(m: re.Match) -> str:
        subcat, page, anchor = m.group(1), m.group(2), m.group(3) or ""
        if subcat not in _SUBCATS:
            return m.group(0)
        local = "faq" if subcat == "frequently-asked-questions" else subcat
        return f"](/docs/{site_slug}/{local}/{page}{anchor})"
    return _REL_LINK_RE.sub(repl, body)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE = "https://doc.16781678.xyz"
REPO = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO / "content" / "docs"

# URL segment → (local folder name, display title). The URL segment is what
# appears in the site's own URL paths; the local folder name is what we write
# under content/docs/<site>/. For every segment not listed here we fall back to
# (segment, segment.replace('-', ' ').title()).
CATEGORY_MAP = {
    "getting-started": ("getting-started", "快速开始"),
    "configuration": ("configuration", "配置指南"),
    "payment": ("payment", "支付集成"),
    "deployment": ("deployment", "部署指南"),
    "video-tutorials": ("video-tutorials", "视频教程"),
    "frequently-asked-questions": ("faq", "常见问题"),
    "others": ("others", "其他"),
}

# Preferred order of subcategories in the sidebar, for sites that publish all
# the standard buckets. Unknown categories get appended at the end in the order
# first discovered.
CATEGORY_ORDER = [
    "getting-started", "configuration", "payment", "deployment",
    "video-tutorials", "faq", "others",
]

# Site slug → display title (shown as the section title on the docs sidebar).
SITE_TITLES = {
    "joyflix": "JoyFlix 手册",
    "nanobanana": "Nano Banana 手册",
    "gamiary": "Gamiary 手册",
    "blog": "Blog 手册",
    "markdown-blog": "Markdown Blog 手册",
    "gpt-image2": "GPT Image 2 手册",
}


# ---------- URL harvest ----------

def harvest_urls(site: str) -> list[str]:
    """Collect all `/<site>/<cat>/<slug>` URLs from the site root AND one page
    per discovered category (to pick up sidebar entries not on the landing)."""
    pattern = re.compile(rf"/{re.escape(site)}/[a-z0-9\-][a-z0-9\-/]*")

    def harvest_page(url: str) -> set[str]:
        try:
            html = fetch_html(url)
        except Exception as e:
            print(f"  [harvest] skip {url}: {e}")
            return set()
        hits = set()
        for m in pattern.findall(html):
            u = m.rstrip("/")
            if u.count("/") < 3:  # /site/cat (no slug) — skip
                continue
            if "/search" in u:
                continue
            hits.add(u)
        return hits

    # First pass: landing page.
    urls = harvest_page(f"{BASE}/{site}")
    # Second pass: one URL per category to catch any missing siblings.
    per_cat: dict[str, str] = {}
    for u in urls:
        parts = u.strip("/").split("/")
        if len(parts) >= 3:
            per_cat.setdefault(parts[1], u)
    for cat, probe_url in per_cat.items():
        urls |= harvest_page(f"{BASE}{probe_url}")
    return sorted(urls)


# ---------- Title detection ----------

_H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


def detect_title(md: str, fallback_slug: str) -> str:
    m = _H1_RE.search(md)
    if m:
        title = m.group(1).strip().strip("'\"")
        if 1 <= len(title) <= 200:
            return title
    return fallback_slug.replace("-", " ").title()


_LEADING_H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def strip_leading_title(md: str, title: str) -> str:
    """Remove a leading `# <title>` line from the body so fumadocs doesn't
    render the same heading twice (once as DocsTitle, once from MDX)."""
    # Only act if the first non-empty line is `# <title>`.
    stripped = md.lstrip("\n")
    lines = stripped.split("\n", 1)
    if not lines:
        return md
    first = lines[0].strip()
    if not first.startswith("# "):
        return md
    if _norm(first[2:]) != _norm(title):
        return md
    rest = lines[1] if len(lines) > 1 else ""
    return rest.lstrip("\n")


# ---------- Per-site processing ----------

def process_site(site: str) -> None:
    print(f"\n##### {site} #####")
    out_root = DOCS_ROOT / site
    out_root.mkdir(parents=True, exist_ok=True)

    # Section index page.
    section_title = SITE_TITLES.get(site, site)
    (out_root / "index.mdx").write_text(
        f"---\ntitle: '{yaml_quote(section_title)}'\n---\n\n"
        f"{section_title}：快速开始、配置、支付、部署与常见问题指南。\n",
        encoding="utf-8",
    )

    urls = harvest_urls(site)
    print(f"  harvested {len(urls)} urls")

    # Group by URL segment → list of (slug, url) preserving harvest order.
    grouped: dict[str, list[tuple[str, str]]] = {}
    for u in urls:
        parts = u.strip("/").split("/")
        if len(parts) < 3:
            continue
        cat_seg = parts[1]
        slug = parts[2]
        grouped.setdefault(cat_seg, []).append((slug, u))

    fail: list[tuple[str, str]] = []
    written_subcats: list[str] = []
    cat_order = [c for c in CATEGORY_ORDER if c in {CATEGORY_MAP.get(k, (k,))[0] for k in grouped}]
    # Walk grouped by preferred URL segment order.
    url_seg_order = [
        seg for seg in ["getting-started", "configuration", "payment", "deployment",
                         "video-tutorials", "frequently-asked-questions", "others"]
        if seg in grouped
    ]
    for seg in grouped:
        if seg not in url_seg_order:
            url_seg_order.append(seg)

    for cat_seg in url_seg_order:
        local_folder, cat_title = CATEGORY_MAP.get(
            cat_seg, (cat_seg, cat_seg.replace("-", " ").title())
        )
        cat_dir = out_root / local_folder
        cat_dir.mkdir(parents=True, exist_ok=True)
        page_slugs: list[str] = []

        for slug, url in grouped[cat_seg]:
            full_url = f"{BASE}{url}"
            try:
                html = fetch_html(full_url)
                md = extract_markdown(html)
                if not md:
                    raise RuntimeError("no markdown chunk found")
            except Exception as e:
                print(f"  [fail] {url} -> {e}")
                fail.append((url, str(e)))
                continue

            title = detect_title(md, slug)
            md = strip_leading_title(md, title)
            body = rewrite_internal_links(md, site)
            body = rewrite_remote_images(body)
            body = rewrite_fence_langs(body)
            body = fix_smart_quotes_in_tags(body)
            body = self_close_void_tags(body)
            body = wrap_bare_esm_lines(body)
            body = escape_prose_html(body)
            out_file = cat_dir / f"{slug}.mdx"
            out_file.write_text(
                f"---\ntitle: '{yaml_quote(title)}'\n---\n\n{body}".rstrip() + "\n",
                encoding="utf-8",
            )
            page_slugs.append(slug)
            time.sleep(0.3)

        (cat_dir / "meta.json").write_text(
            json.dumps({"title": cat_title, "pages": page_slugs}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        written_subcats.append(local_folder)
        print(f"  [{local_folder}] {len(page_slugs)} page(s)")

    # `root: true` makes fumadocs treat this folder as an independent sidebar
    # root. Without it, the folder's tree gets merged into the parent docs tree
    # and the sidebar on every page under this site falls back to the full
    # `content/docs/` tree (showing AI 出海手册 categories instead of this
    # handbook's own categories).
    (out_root / "meta.json").write_text(
        json.dumps({"title": section_title, "root": True, "pages": written_subcats}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if fail:
        print(f"  FAILED ({len(fail)}):")
        for u, e in fail:
            print(f"    {u} -> {e}")


# ---------- Entrypoint ----------

def main() -> None:
    if len(sys.argv) < 2:
        sites = list(SITE_TITLES.keys())
    else:
        sites = sys.argv[1:]
    for site in sites:
        process_site(site)
    print("\n=== all done ===")


if __name__ == "__main__":
    main()
