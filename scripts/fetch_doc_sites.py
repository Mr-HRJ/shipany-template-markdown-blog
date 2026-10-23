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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import html as _html
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path
from typing import Callable
from urllib.parse import quote, urlparse

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
from fix_heading_links import HEADING_RE, fix_heading_text  # noqa: E402

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
    "sea": "AI 出海手册",
    "shipany-two": "ShipAny Two 手册",
    "joyflix": "JoyFlix 手册",
    "nanobanana": "Nano Banana 手册",
    "gamiary": "Gamiary 手册",
    "blog": "Blog 手册",
    "markdown-blog": "Markdown Blog 手册",
    "gpt-image2": "GPT Image 2 手册",
}

# `/sea` is the source for the existing root-level "AI 出海手册", rather
# than an independent handbook under `content/docs/sea`.  Keep its source URL
# segments mapped to the established local folders so already-indexed routes
# remain stable while titles, bodies, dates and sidebar order are refreshed.
SEA_CATEGORY_MAP = {
    "readme": ("must-read", "网站出海必读"),
    "need": ("ideas", "找需求"),
    "data": ("analytics", "数据分析"),
    "dev": ("dev", "开发"),
    "pay": ("payment", "支付"),
    "seo": ("seo", "Seo"),
    "saas-seo": ("saas-seo", "AI 工具站 SEO 小册子"),
    "geo": ("geo", "GEO"),
    "external-links": ("backlink", "外链"),
    "flow": ("traffic", "流量"),
    "ads": ("ads", "Ads"),
    "other": ("misc", "其他"),
    "review": ("review", "复盘"),
}

# These are distinct source articles with exactly the same sidebar title.
# Bind their verified identities explicitly without changing the old route.
SEA_ROUTE_OVERRIDES = {
    "/sea/geo/geo-optimization-playbook-ai-search-era": "geo/GEO-AI-搜索时代的新流量入口.md",
    "/sea/geo/geo-ai-search-door": "geo/geo-ai-search-door.md",
}

_NEXT_PUSH_RE = re.compile(
    r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)', re.DOTALL
)


def decode_rsc_payload(page_html: str) -> str:
    """Decode all Next.js flight string chunks into one searchable payload."""
    chunks: list[str] = []
    for literal in _NEXT_PUSH_RE.findall(page_html):
        try:
            chunks.append(json.loads(literal))
        except json.JSONDecodeError:
            continue
    return "".join(chunks)


def extract_page_tree(page_html: str, site: str) -> list[tuple[str, str]]:
    """Read page nodes, including React labels and lazy Flight references."""
    payload = decode_rsc_payload(page_html)
    decoder = json.JSONDecoder()
    records = {
        match.group(1): match.end()
        for match in re.finditer(r"(?m)^([0-9a-f]+):", payload)
    }

    def label(value: object, seen: frozenset[str] = frozenset()) -> str:
        if isinstance(value, str):
            reference = re.fullmatch(r"\$L?([0-9a-f]+)", value)
            if reference:
                record = reference.group(1)
                if record in seen or record not in records:
                    raise RuntimeError(f"unresolved page title reference: {value}")
                try:
                    resolved, _ = decoder.raw_decode(payload, records[record])
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"invalid page title reference: {value}") from exc
                return label(resolved, seen | {record})
            return value[1:] if value.startswith("$$") else value
        if isinstance(value, list):
            if len(value) >= 4 and value[0] == "$" and isinstance(value[3], dict):
                props = value[3]
                key = str(value[2] or "")
                if (
                    key.startswith(("new-label-", "child-update-dot-"))
                    or props.get("aria-hidden") is True
                ):
                    return ""
                return label(props.get("children", ""), seen)
            return "".join(label(child, seen) for child in value)
        if value is None:
            return ""
        raise RuntimeError(f"unsupported page title value: {type(value).__name__}")

    trees: list[dict] = []
    for match in re.finditer(r'"tree"\s*:\s*', payload):
        try:
            tree, _ = decoder.raw_decode(payload, match.end())
        except json.JSONDecodeError:
            continue
        if isinstance(tree, dict) and isinstance(tree.get("children"), list):
            trees.append(tree)
    if not trees:
        raise RuntimeError(f"/{site} complete page tree not found")

    inventories: list[list[tuple[str, str]]] = []
    for tree in trees:
        items: list[tuple[str, str]] = []
        seen_urls: set[str] = set()

        def visit(node: dict) -> None:
            if node.get("type") == "page":
                url = node.get("url", "")
                if isinstance(url, str) and url.startswith(f"/{site}/"):
                    title = label(node.get("name")).strip()
                    if not title or title.startswith("$L"):
                        raise RuntimeError(f"empty or unresolved page title: {url}")
                    url = url.rstrip("/")
                    if url not in seen_urls:
                        items.append((title, url))
                        seen_urls.add(url)
            index = node.get("index")
            if isinstance(index, dict):
                visit(index)
            for child in node.get("children", []):
                if isinstance(child, dict):
                    visit(child)

        visit(tree)
        if items:
            inventories.append(items)
    if not inventories or any(items != inventories[0] for items in inventories):
        raise RuntimeError(f"/{site} page tree is empty or inconsistent")
    return inventories[0]


def harvest_page_tree(site: str) -> list[tuple[str, str]]:
    """Return exact `(sidebar title, URL)` pairs from the root RSC page tree.

    Reading the decoded page tree avoids the shortened links emitted by cards
    in the rendered HTML.  Those shortened links caused the older harvester to
    silently miss valid `/sea` articles.
    """
    previous: list[tuple[str, str]] | None = None

    # Cloudflare occasionally serves an incomplete streamed RSC response even
    # with HTTP 200. Never synchronize from a largest-response fallback:
    # two complete inventories must agree on both titles and URLs.
    for attempt in range(4):
        page_html = fetch_html(f"{BASE}/{site}")
        items = extract_page_tree(page_html, site)
        if items == previous:
            return items
        previous = items
        if attempt < 3:
            time.sleep(0.25)
    raise RuntimeError(f"/{site} page tree did not stabilize after four fetches")


# ---------- URL harvest ----------

def harvest_urls(site: str) -> list[str]:
    """Collect all `/<site>/<cat>/<slug>` URLs in source sidebar order.

    Strategy: in fumadocs SSR the full sidebar is rendered before the article
    body in document order, so the order in which URLs first appear in a leaf
    page's HTML matches the sidebar's authored order. We probe one leaf per
    discovered category and keep first-appearance order. Sorting alphabetically
    here would scramble the author's intent.
    """
    # Prefer the canonical page tree. Fall back to the older HTML-link probes
    # for deployments whose RSC payload does not expose sidebar nodes.
    try:
        tree_urls = [
            url
            for _, url in harvest_page_tree(site)
            if len(url.strip("/").split("/")) >= 3
        ]
        if tree_urls:
            return tree_urls
    except Exception as e:
        print(f"  [harvest] page-tree fallback for {site}: {e}")

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


# ---------- `/sea` root-handbook synchronization ----------

_SEA_FRONTMATTER_TITLE_RE = re.compile(r"(?m)^title:\s*(.+?)\s*$")
_SEA_MD_IMAGE_RE = re.compile(
    r"(!\[[^\]]*\]\()(https?://[^)\s]+)((?:\s+\"[^\"]*\")?\))"
)
_SEA_HTML_IMAGE_RE = re.compile(r'(<img\s+[^>]*?src=")(https?://[^"]+)(")')
_SEA_IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif"
}


def _norm_sea_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    for old, new in {
        "“": "", "”": "", "‘": "", "’": "", "「": "", "」": "",
        "『": "", "』": "", "，": ",", "。": ".", "：": ":",
        "；": ";", "（": "(", "）": ")", "【": "[", "】": "]",
        "？": "?", "！": "!", "、": ",", "／": "/", "→": "-",
        "–": "-", "—": "-",
    }.items():
        value = value.replace(old, new)
    return re.sub(r"[\s\-_./,:;()\[\]?!#&+$'\"]+", "", value)


def _sea_file_slug(title: str, max_len: int = 18) -> str:
    slug = re.sub(r"[^A-Za-z0-9一-鿿-]+", "-", title)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug or "untitled"


def _read_local_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = _SEA_FRONTMATTER_TITLE_RE.search(text[:4000])
    if not match:
        raise RuntimeError(f"missing frontmatter title: {path.relative_to(REPO)}")
    title = match.group(1).strip()
    if len(title) >= 2 and title[0] == title[-1] and title[0] in "'\"":
        title = title[1:-1]
    return title.replace("''", "'")


def _source_dates(page_html: str) -> tuple[str | None, str | None]:
    payload = decode_rsc_payload(page_html)

    def parse(label: str) -> str | None:
        match = re.search(rf"{label}:\s*(\d{{2}}/\d{{2}}/\d{{4}})", payload)
        if not match:
            return None
        return datetime.strptime(match.group(1), "%m/%d/%Y").date().isoformat()

    return parse("Created"), parse("Updated")


def _normalize_sea_markdown(body: str) -> str:
    """Keep Markdown hard breaks without importing trailing whitespace."""
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            lines.append(line)
        elif in_fence:
            lines.append(line)
        else:
            trimmed = line.rstrip(" \t")
            heading = HEADING_RE.match(trimmed)
            if heading:
                trimmed = heading.group(1) + fix_heading_text(heading.group(2))
            if trimmed and line.endswith("  ") and not re.match(r"^#{1,6}(?:\s|$)", stripped):
                # GFM otherwise treats the hard-break backslash as part of a
                # bare URL, producing links ending in %5C after compilation.
                url_line = re.fullmatch(r"(\s*)(https?://[^\s<>]+)", trimmed)
                if url_line:
                    trimmed = f"{url_line.group(1)}<{url_line.group(2)}>"
                trimmed += "\\"
            lines.append(trimmed)
    return "\n".join(lines)


def _fetch_sea_article(item: dict[str, object]) -> dict[str, object]:
    source_path = str(item["source_path"])
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            page_html = fetch_html(f"{BASE}{source_path}")
            body = extract_markdown(page_html)
            if not body:
                raise RuntimeError("no markdown chunk found")
            body = _normalize_sea_markdown(rewrite_fence_langs(body))
            created, updated = _source_dates(page_html)
            if not created:
                raise RuntimeError("source Created date not found")
            return {
                "body": body.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n",
                "date": created,
                "updated": updated,
            }
        except Exception as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(attempt)
    raise RuntimeError(f"{source_path}: {last_error}")


def _load_r2_compare_config() -> tuple[str, str, dict[str, str]] | None:
    creds_path = REPO / "scripts" / ".r2-creds.json"
    if not creds_path.exists():
        return None
    creds = json.loads(creds_path.read_text(encoding="utf-8"))
    public_base = str(creds.get("public_base", "")).rstrip("/")
    prefix = str(creds.get("key_prefix", "")).strip("/")
    if not public_base:
        return None
    manifest_path = REPO / "scripts" / "image_migration_manifest.json"
    known_urls: dict[str, str] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        known_urls = {
            url: str(value["public_url"])
            for url, value in manifest.items()
            if value.get("status") == "ok" and value.get("public_url")
        }
    return public_base, prefix, known_urls


def _r2_candidate(
    url: str, config: tuple[str, str, dict[str, str]] | None
) -> str:
    if not config:
        return url
    public_base, prefix, known_urls = config
    if urlparse(url).hostname == urlparse(public_base).hostname:
        return url
    if url in known_urls:
        return known_urls[url]
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix not in _SEA_IMAGE_EXTENSIONS:
        suffix = ".jpg"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    key = f"{digest}{suffix}"
    if prefix:
        key = f"{prefix}/{key}"
    return f"{public_base}/{key}"


def _rewrite_sea_image_urls(
    body: str,
    config: tuple[str, str, dict[str, str]] | None,
    should_reuse: Callable[[str], bool] | None = None,
) -> str:
    def replace(match: re.Match) -> str:
        original = match.group(2)
        candidate = _r2_candidate(original, config)
        replacement = candidate if should_reuse is None or should_reuse(candidate) else original
        return f"{match.group(1)}{replacement}{match.group(3)}"

    body = _SEA_HTML_IMAGE_RE.sub(replace, body)
    return _SEA_MD_IMAGE_RE.sub(replace, body)


def _rewrite_sea_internal_links(body: str, source_to_local: dict[str, str]) -> str:
    # This legacy link omits the ShipAny Two handbook prefix on the source.
    body = re.sub(
        r'''(\]\(|href=["'])(?:''' + re.escape(BASE)
        + r''')?/payment/how-china-person-pay(?=[#)"'\s])''',
        r"\1/docs/shipany-two/payment/how-china-person-pay",
        body,
    )
    # Longest first protects against one source slug being a prefix of another.
    for source_path in sorted(source_to_local, key=len, reverse=True):
        local_url = source_to_local[source_path]
        variants = [f"{BASE}{source_path}", source_path]
        if source_path.startswith("/sea/"):
            variants.append(source_path[len("/sea"):])
        for old in variants:
            body = body.replace(f"]({old}", f"]({local_url}")
            body = body.replace(f'href="{old}', f'href="{local_url}')
            body = body.replace(f"href='{old}", f"href='{local_url}")
    return body


def _render_sea_doc(
    title: str, date: str, updated: str | None, body: str
) -> str:
    frontmatter = ["---", f"title: '{yaml_quote(title)}'", f"date: '{date}'"]
    if updated:
        frontmatter.append(f"updated: '{updated}'")
    frontmatter.extend(["---", ""])
    return "\n".join(frontmatter) + "\n" + body.rstrip() + "\n"


def process_sea() -> None:
    """Synchronize `/sea` into the existing root AI handbook in-place."""
    print("\n##### sea (root AI handbook) #####")
    tree = harvest_page_tree("sea")
    if not tree:
        raise RuntimeError("/sea page tree is empty")
    # The source still serves its README landing page even when it is omitted
    # from the sidebar. Preserve the existing entry URL without adding a
    # sidebar item absent from the source tree.
    sidebar_urls = {url for _, url in tree}
    if "/sea/readme" not in sidebar_urls:
        tree = [("网站出海必读", "/sea/readme")] + tree

    expected_category_order = list(SEA_CATEGORY_MAP)
    found_category_order: list[str] = []
    source_items: list[dict[str, object]] = []
    seen_source_urls: set[str] = set()
    source_titles: dict[tuple[str, str], list[str]] = {}
    pinned_paths: dict[str, Path] = {}
    pinned_routes: set[tuple[str, str]] = set()

    for title, source_path in tree:
        if source_path in seen_source_urls:
            continue
        seen_source_urls.add(source_path)
        parts = source_path.strip("/").split("/")
        if source_path == "/sea/readme":
            source_category = "readme"
            local_folder = "must-read"
            category_title = "网站出海必读"
            if source_category not in found_category_order:
                found_category_order.append(source_category)
        elif len(parts) == 3 and parts[0] == "sea" and parts[1] in SEA_CATEGORY_MAP:
            source_category = parts[1]
            local_folder, category_title = SEA_CATEGORY_MAP[source_category]
            if source_category not in found_category_order:
                found_category_order.append(source_category)
        else:
            raise RuntimeError(f"unmapped /sea article: {source_path}")

        title_key = (local_folder, _norm_sea_title(title))
        source_titles.setdefault(title_key, []).append(source_path)
        override = SEA_ROUTE_OVERRIDES.get(source_path)
        if override:
            relative = Path(override)
            path = DOCS_ROOT / relative
            if (
                relative.is_absolute() or len(relative.parts) != 2
                or relative.parts[0] != local_folder
                or relative.suffix not in {".md", ".mdx"}
                or not path.resolve().is_relative_to(DOCS_ROOT.resolve())
            ):
                raise RuntimeError(f"invalid /sea route override: {source_path}")
            route = (local_folder, relative.stem)
            if route in pinned_routes:
                raise RuntimeError(f"duplicate /sea route override: {source_path}")
            pinned_routes.add(route)
            pinned_paths[source_path] = path
        source_items.append({
            "title": title,
            "source_path": source_path,
            "source_category": source_category,
            "local_folder": local_folder,
            "category_title": category_title,
        })

    for key, urls in source_titles.items():
        if len(urls) > 1 and any(url not in pinned_paths for url in urls):
            raise RuntimeError(f"duplicate source title in {key[0]}: {urls}")
    for source_path, relative in SEA_ROUTE_OVERRIDES.items():
        if source_path not in seen_source_urls and (DOCS_ROOT / relative).exists():
            raise RuntimeError(f"pinned /sea source missing; verify removal first: {source_path}")

    if found_category_order != expected_category_order:
        raise RuntimeError(
            f"unexpected /sea category order: {found_category_order}; "
            f"expected {expected_category_order}"
        )
    if not source_items or source_items[0]["source_path"] != "/sea/readme":
        raise RuntimeError("/sea readme is missing or not first in the page tree")

    local_folders = [value[0] for value in SEA_CATEGORY_MAP.values()]
    existing_by_key: dict[tuple[str, str], Path] = {}
    pinned_local_keys: set[tuple[str, str]] = set()
    all_existing: set[Path] = set()
    occupied_stems: dict[str, set[str]] = {}
    for local_folder in local_folders:
        folder = DOCS_ROOT / local_folder
        occupied_stems[local_folder] = set()
        try:
            existing_paths = sorted(folder.iterdir())
        except FileNotFoundError:
            # New source categories have no local directory until every source
            # page has fetched successfully and its first article is written.
            existing_paths = []
        for path in existing_paths:
            if path.suffix.lower() not in {".md", ".mdx"}:
                continue
            all_existing.add(path)
            occupied_stems[local_folder].add(path.stem)
            key = (local_folder, _norm_sea_title(_read_local_title(path)))
            if path in pinned_paths.values():
                if key in existing_by_key:
                    raise RuntimeError(f"duplicate local title: {path.relative_to(REPO)}")
                pinned_local_keys.add(key)
                continue
            if key in existing_by_key or key in pinned_local_keys:
                raise RuntimeError(f"duplicate local title: {path.relative_to(REPO)}")
            existing_by_key[key] = path

    for path in pinned_paths.values():
        if path not in all_existing and path.stem in occupied_stems[path.parent.name]:
            raise RuntimeError(f"pinned /sea route already occupied: {path.relative_to(REPO)}")
        occupied_stems[path.parent.name].add(path.stem)

    used_existing: set[Path] = set()
    for item in source_items:
        local_folder = str(item["local_folder"])
        key = (local_folder, _norm_sea_title(str(item["title"])))
        path = pinned_paths.get(str(item["source_path"])) or existing_by_key.get(key)
        if path in all_existing:
            used_existing.add(path)
        elif path is None:
            base = _sea_file_slug(str(item["title"]))
            stem = base
            suffix = 2
            while stem in occupied_stems[local_folder]:
                stem = f"{base}-{suffix}"
                suffix += 1
            occupied_stems[local_folder].add(stem)
            path = DOCS_ROOT / local_folder / f"{stem}.md"
        item["local_path"] = path

    stale_local = sorted(all_existing - used_existing)
    source_to_local = {
        str(item["source_path"]): (
            f"/docs/{item['local_folder']}/"
            f"{quote(Path(item['local_path']).stem, safe='-._~')}"
        )
        for item in source_items
    }

    print(
        f"  source tree: {len(source_items)} page(s); "
        f"local before sync: {len(all_existing)} page(s)"
    )
    print("  fetching all source pages (6 workers)...", flush=True)
    fetched: dict[str, dict[str, object]] = {}
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        future_to_item = {pool.submit(_fetch_sea_article, item): item for item in source_items}
        completed = 0
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                fetched[str(item["source_path"])] = future.result()
            except Exception as exc:
                failures.append(str(exc))
            completed += 1
            if completed % 20 == 0 or completed == len(source_items):
                print(f"  fetched {completed}/{len(source_items)}", flush=True)
    if failures:
        raise RuntimeError("source fetch failed:\n  " + "\n  ".join(failures))

    r2_config = _load_r2_compare_config()
    added: list[tuple[str, str]] = []
    updated_docs: list[tuple[str, str]] = []
    unchanged = 0
    pages_by_folder: dict[str, list[str]] = {folder: [] for folder in local_folders}

    for item in source_items:
        title = str(item["title"])
        source_path = str(item["source_path"])
        local_folder = str(item["local_folder"])
        local_path = Path(item["local_path"])
        result = fetched[source_path]
        body = _rewrite_sea_internal_links(str(result["body"]), source_to_local)
        new_text = _render_sea_doc(
            title,
            str(result["date"]),
            str(result["updated"]) if result["updated"] else None,
            body,
        )
        if source_path in sidebar_urls:
            pages_by_folder[local_folder].append(local_path.stem)

        current = local_path.read_text(encoding="utf-8") if local_path.exists() else None
        comparable = _rewrite_sea_image_urls(new_text, r2_config)
        if current is not None and _normalize_sea_markdown(current) == comparable:
            unchanged += 1
            continue

        if current is not None:
            # Reuse only deterministic R2 URLs already referenced by this page;
            # genuinely new source images remain external for migrate_images.py.
            new_text = _rewrite_sea_image_urls(
                new_text,
                r2_config,
                should_reuse=lambda candidate, old=current: candidate in old,
            )
            updated_docs.append((local_folder, title))
        else:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            added.append((local_folder, title))
        local_path.write_text(new_text, encoding="utf-8")

    for path in stale_local:
        path.unlink()

    category_titles = {"must-read": "网站出海必读"}
    category_titles.update({folder: title for folder, title in SEA_CATEGORY_MAP.values()})
    for folder in local_folders:
        meta_path = DOCS_ROOT / folder / "meta.json"
        meta_text = json.dumps(
            {"title": category_titles[folder], "pages": pages_by_folder[folder]},
            ensure_ascii=False,
            indent=2,
        ) + "\n"
        if not meta_path.exists() or meta_path.read_text(encoding="utf-8") != meta_text:
            meta_path.write_text(meta_text, encoding="utf-8")

    root_meta = json.dumps(
        {"title": "AI 出海手册", "pages": local_folders},
        ensure_ascii=False,
        indent=2,
    ) + "\n"
    root_meta_path = DOCS_ROOT / "meta.json"
    if root_meta_path.read_text(encoding="utf-8") != root_meta:
        root_meta_path.write_text(root_meta, encoding="utf-8")

    print(
        f"  sync result: {len(added)} added, {len(updated_docs)} updated, "
        f"{unchanged} unchanged, {len(stale_local)} removed"
    )
    for folder, title in added:
        print(f"    [add:{folder}] {title}")
    for folder, title in updated_docs:
        print(f"    [update:{folder}] {title}")
    for path in stale_local:
        print(f"    [remove] {path.relative_to(REPO)}")


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
        if site == "sea":
            process_sea()
        else:
            process_site(site)
    print("\n=== all done ===")


if __name__ == "__main__":
    main()
