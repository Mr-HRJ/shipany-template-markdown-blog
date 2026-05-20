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
import html as _html
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
    """Collect all `/<site>/<cat>/<slug>` URLs in source sidebar order.

    Strategy: in fumadocs SSR the full sidebar is rendered before the article
    body in document order, so the order in which URLs first appear in a leaf
    page's HTML matches the sidebar's authored order. We probe one leaf per
    discovered category and keep first-appearance order. Sorting alphabetically
    here would scramble the author's intent.
    """
    pattern = re.compile(rf"/{re.escape(site)}/[a-z0-9\-][a-z0-9\-/]*")

    def harvest_page(url: str) -> list[str]:
        try:
            html = fetch_html(url)
        except Exception as e:
            print(f"  [harvest] skip {url}: {e}")
            return []
        seen_local: set[str] = set()
        ordered: list[str] = []
        for m in pattern.findall(html):
            u = m.rstrip("/")
            if u.count("/") < 3 or "/search" in u:
                continue
            if u in seen_local:
                continue
            seen_local.add(u)
            ordered.append(u)
        return ordered

    # Pass 1: handbook root URL — its set of slugs is the source of truth
    # (only published articles are linked from the root), but URLs may be
    # truncated in hero/preview cards and the across-category order is the
    # only reliable signal here.
    landing = harvest_page(f"{BASE}/{site}")
    site_prefix = f"/{site}/"

    # Pass 2: probe one leaf for full (un-truncated) URLs and the canonical
    # within-category order. Leaf may also surface stale sidebar entries
    # (404 slugs) and cross-handbook "related" links — we whitelist using
    # landing later.
    leaf_list: list[str] = []
    for probe in landing:
        result = harvest_page(f"{BASE}{probe}")
        candidates = [u for u in result if u.startswith(site_prefix)]
        if len(candidates) >= max(len(landing) - 5, 1):
            leaf_list = candidates
            break
    if not leaf_list:
        leaf_list = [u for u in landing if u.startswith(site_prefix)]

    # Expand truncated landing URLs to their full leaf counterpart.
    leaf_set = set(leaf_list)
    valid: set[str] = set()
    for u in landing:
        if not u.startswith(site_prefix):
            continue
        if u in leaf_set:
            valid.add(u)
        else:
            # Truncated landing URL like /payment/how-to-tran — pick the
            # shortest leaf URL that starts with it.
            matches = sorted(
                (f for f in leaf_set if f.startswith(u)),
                key=len,
            )
            if matches:
                valid.add(matches[0])

    # Take within-category order from leaf_list (skipping URLs not in valid),
    # then re-order categories by first appearance in landing.
    by_cat: dict[str, list[str]] = {}
    seen_in_cat: dict[str, set[str]] = {}
    for u in leaf_list:
        if u not in valid:
            continue
        parts = u.strip("/").split("/")
        if len(parts) < 3:
            continue
        cat = parts[1]
        if u in seen_in_cat.setdefault(cat, set()):
            continue
        seen_in_cat[cat].add(u)
        by_cat.setdefault(cat, []).append(u)

    cat_order_from_landing: dict[str, int] = {}
    for i, u in enumerate(landing):
        parts = u.strip("/").split("/")
        if len(parts) >= 3:
            cat_order_from_landing.setdefault(parts[1], i)

    cats_sorted = sorted(
        by_cat,
        key=lambda c: cat_order_from_landing.get(c, len(landing) + 1),
    )
    return [u for c in cats_sorted for u in by_cat[c]]


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


_SIDEBAR_ANCHOR_RE = re.compile(r'<a[^>]*href="(/[^"]+)"[^>]*>(.*?)</a>', re.S)
_STRIP_TAGS_RE = re.compile(r"<[^>]+>")


def harvest_sidebar_titles(
    site: str, grouped: dict[str, list[tuple[str, str]]]
) -> dict[tuple[str, str], str]:
    """For each category, fetch its first article's leaf page and read sidebar
    anchor text. The source site renders link text only for the currently-
    expanded category on a leaf page, so we probe one leaf per category to
    cover everything. Returns {(cat_seg, slug): label}.
    """
    result: dict[tuple[str, str], str] = {}
    for cat_seg, articles in grouped.items():
        if not articles:
            continue
        _, probe_path = articles[0]
        try:
            page_html = fetch_html(f"{BASE}{probe_path}")
        except Exception as e:
            print(f"  [sidebar-probe] skip {probe_path}: {e}")
            continue
        for m in _SIDEBAR_ANCHOR_RE.finditer(page_html):
            href = m.group(1).rstrip("/")
            parts = href.strip("/").split("/")
            if len(parts) < 3 or parts[0] != site or parts[1] != cat_seg:
                continue
            slug = parts[2]
            text = _html.unescape(_STRIP_TAGS_RE.sub("", m.group(2))).strip()
            text = re.sub(r"\s+", " ", text)
            if text and (cat_seg, slug) not in result:
                result[(cat_seg, slug)] = text
        time.sleep(0.2)
    return result


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

    # Probe one leaf per category to scrape the real sidebar labels. Without
    # this we'd write the body H1 (or slug-titlecase fallback) into frontmatter,
    # which makes the sidebar show generic strings like "写在前面" for any
    # article whose body starts with that heading.
    sidebar_titles = harvest_sidebar_titles(site, grouped)
    print(f"  scraped {len(sidebar_titles)} sidebar label(s)")

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

            detected = detect_title(md, slug)
            sidebar = sidebar_titles.get((cat_seg, slug))
            title = sidebar or detected
            # Only strip the body H1 when we're using it AS the title — keeping
            # it in the body otherwise prevents the page heading from getting
            # lost when sidebar text overrides title.
            if not sidebar:
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
