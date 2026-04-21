"""Batch-convert AI-chuhai/*/*.pdf to content/docs/{slug}/*.mdx with images.

Run:
    python scripts/convert_pdfs.py
"""

import hashlib
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path

import pymupdf4llm

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
SRC = Path("C:/Users/VULCAN/Desktop/AI-chuhai")
DOCS = REPO / "content" / "docs"
IMG_ROOT = REPO / "public" / "docs-images"

CATEGORY_SLUG = {
    "Ads": "ads",
    "GEO": "geo",
    "Seo": "seo",
    "其他": "misc",
    "复盘": "review",
    "外链": "backlink",
    "开发": "dev",
    "找需求": "ideas",
    "支付": "payment",
    "数据分析": "analytics",
    "流量": "traffic",
}

CATEGORY_TITLE = {
    "ads": "Ads 投流",
    "geo": "GEO 优化",
    "seo": "SEO",
    "misc": "其他",
    "review": "复盘",
    "backlink": "外链",
    "dev": "开发",
    "ideas": "找需求",
    "payment": "支付",
    "analytics": "数据分析",
    "traffic": "流量",
}


def file_slug(name: str, max_len: int = 18) -> str:
    """Allowlist slug: keep a-zA-Z0-9, CJK Unified Ideographs, and dashes only.
    Everything else -> dash (then collapsed). Truncate to max_len chars so the
    URL-encoded Windows path stays under MAX_PATH (260). The allowlist guarantees
    the slug matches Fumadocs' internal URL normalization."""
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9一-鿿-]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).strip("-")
    if len(stem) > max_len:
        stem = stem[:max_len].rstrip("-")
    return stem or "untitled"


def _normalize_cjk_compat(text: str) -> str:
    """NFKC-map ONLY CJK compatibility + Kangxi radicals blocks. Leaves
    fullwidth punctuation and Chinese quotation marks intact."""
    def is_compat(cp: int) -> bool:
        return (
            0x2E80 <= cp <= 0x2FDF  # CJK Radicals Supp + Kangxi Radicals
            or 0xF900 <= cp <= 0xFAFF  # CJK Compat Ideographs
            or 0x2F800 <= cp <= 0x2FA1F  # CJK Compat Ideographs Supp
        )

    out = []
    for ch in text:
        if is_compat(ord(ch)):
            out.append(unicodedata.normalize("NFKC", ch))
        else:
            out.append(ch)
    return "".join(out)


def post_process(md: str, img_prefix: str, title: str) -> str:
    """Clean pymupdf4llm output: CJK-compat normalize, drop boilerplate, merge
    split headings, collapse mid-paragraph line breaks, demote false-positive
    headings, fix image paths."""
    # 1) Normalize CJK compatibility chars only
    md = _normalize_cjk_compat(md)

    # 2) rewrite image paths to public /docs-images/{cat}/{slug}/...
    md = re.sub(
        r"!\[\]\(([^)]+)\)",
        lambda m: f"![]({img_prefix}/{Path(m.group(1)).name})",
        md,
    )

    lines = md.split("\n")
    cleaned: list[str] = []

    # 3) drop leading junk: "SEA" header + English slug line that PDFs prefix
    i = 0
    while i < len(lines) and lines[i].strip() in ("", "SEA"):
        i += 1
    # English-slug line pattern: lowercase letters, digits, dashes only
    if i < len(lines) and re.fullmatch(r"[a-z0-9-]{8,}\s*", lines[i]):
        i += 1
    # 4) drop first H2 that equals the frontmatter title (avoid dup h1+h2)
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].startswith("## "):
        h2 = lines[i][3:].strip().rstrip()
        if h2 == title.strip():
            i += 1

    cleaned = lines[i:]

    # 5) demote false-positive headings FIRST — pymupdf4llm misclassifies
    # font-sized prose as h2. Demote lines whose body reads like a sentence or
    # a list-intro (ends with 。, contains 。 inside, or ends with : / ：).
    demoted: list[str] = []
    for line in cleaned:
        if line.startswith("## "):
            body = line[3:].strip()
            is_prose = (
                body.endswith("。")
                or "。" in body
                or body.endswith(":")
                or body.endswith("：")
            )
            if is_prose:
                demoted.append(body)
                continue
        demoted.append(line)

    # Skip heading merge: auto-merging split headings is ambiguous (same shape as
    # two legitimate sibling headings). Prefer leaving occasional split h2s over
    # risking wrong semantic merges.
    text = "\n".join(demoted)

    # 6) drop orphan bullet items: "- 一" or "- <single CJK char>" on its own line
    text = re.sub(r"(?m)^-\s+[一-鿿]\s*$\n?", "", text)

    # 7) collapse mid-sentence line breaks between CJK (keep paragraph breaks)
    text = re.sub(r"([一-鿿，。！？；：、）】》])\n(?!\n)(?=[一-鿿])", r"\1", text)

    # 8) trim trailing whitespace on every line
    text = "\n".join(l.rstrip() for l in text.split("\n"))

    # 9) collapse 3+ blank lines to max 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip() + "\n"


def _unique_slug(cat_slug: str, slug: str, seen: dict) -> str:
    key = (cat_slug, slug)
    n = seen.get(key, 0) + 1
    seen[key] = n
    return slug if n == 1 else f"{slug}-{n}"


_SEEN: dict = {}


def convert_one(pdf: Path, cat_slug: str) -> tuple[Path, int]:
    slug = _unique_slug(cat_slug, file_slug(pdf.name), _SEEN)
    img_slug = hashlib.sha1(pdf.stem.encode("utf-8")).hexdigest()[:10]
    img_dir = IMG_ROOT / cat_slug / img_slug
    img_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        safe_pdf = Path(td) / "in.pdf"
        safe_pdf.write_bytes(pdf.read_bytes())
        md = pymupdf4llm.to_markdown(
            str(safe_pdf),
            write_images=True,
            image_path=str(img_dir),
            image_format="png",
            dpi=150,
        )
    img_prefix = f"/docs-images/{cat_slug}/{img_slug}"
    md = post_process(md, img_prefix, pdf.stem)

    # frontmatter — YAML-safe: single-quote title, escape inner single quotes
    title = pdf.stem.replace("'", "''")
    fm = f"---\ntitle: '{title}'\n---\n\n"
    out = DOCS / cat_slug / f"{slug}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fm + md, encoding="utf-8")

    img_count = len(list(img_dir.iterdir()))
    if img_count == 0:
        img_dir.rmdir()
    return out, img_count


def main():
    if not SRC.exists():
        sys.exit(f"missing source: {SRC}")

    total_pdf = 0
    total_img = 0
    errors = []
    for cat_zh, cat_en in CATEGORY_SLUG.items():
        cat_dir = SRC / cat_zh
        if not cat_dir.exists():
            print(f"[skip] {cat_zh} not found")
            continue
        pdfs = sorted(cat_dir.glob("*.pdf"))
        print(f"[{cat_en}] {len(pdfs)} pdf(s)")
        for pdf in pdfs:
            try:
                out, n_img = convert_one(pdf, cat_en)
                total_pdf += 1
                total_img += n_img
                print(f"  OK  {pdf.name} -> {out.relative_to(REPO)} ({n_img} img)")
            except Exception as e:
                errors.append((pdf, str(e)))
                print(f"  ERR {pdf.name}: {e}")

    print(f"\n=== done: {total_pdf} pdf, {total_img} img, {len(errors)} err ===")
    if errors:
        for pdf, msg in errors:
            print(f"  - {pdf}: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
