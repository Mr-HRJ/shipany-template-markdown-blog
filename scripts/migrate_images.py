"""Migrate all external <img src="..."> URLs in content/docs/**/*.md to
Cloudflare R2 and rewrite the markdown to point at the R2 public URL.

Usage:
    python scripts/migrate_images.py           # run migration
    python scripts/migrate_images.py --dry-run # preview only, no upload

Idempotent: a manifest at scripts/image_migration_manifest.json maps
original_url -> {key, public_url, status}. Re-runs skip already-uploaded URLs.
"""

import argparse
import hashlib
import json
import mimetypes
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import boto3
import requests
from botocore.config import Config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "content" / "docs"
CREDS_PATH = REPO / "scripts" / ".r2-creds.json"
MANIFEST_PATH = REPO / "scripts" / "image_migration_manifest.json"

IMG_SRC_RE = re.compile(r'(<img\s+[^>]*?src=")(https?://[^"]+)(")')
MD_IMG_RE = re.compile(r'(!\[[^\]]*\]\()(https?://[^)\s]+)((?:\s+"[^"]*")?\))')

HEADERS = {
    # Mimic a normal browser — some hosts (bigrock, etc.) block empty UA.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

EXT_BY_CT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/bmp": ".bmp",
    "image/avif": ".avif",
}


def load_creds() -> dict:
    if not CREDS_PATH.exists():
        sys.exit(f"missing {CREDS_PATH}")
    return json.loads(CREDS_PATH.read_text(encoding="utf-8"))


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(m: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def url_key(url: str, ext: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return digest + ext


def guess_ext(url: str, content_type: str | None) -> str:
    if content_type:
        ct = content_type.split(";", 1)[0].strip().lower()
        if ct in EXT_BY_CT:
            return EXT_BY_CT[ct]
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif"}:
        return ".jpeg" if suffix == ".jpeg" else suffix
    return ".jpg"  # sensible default


def collect_urls() -> tuple[list[str], dict[str, list[Path]]]:
    """Return (unique_urls, url_to_files). Markdown-style `![](url)` shouldn't
    appear after convert_markdown.py, but include it for safety."""
    url_files: dict[str, list[Path]] = {}
    for md in sorted(DOCS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        urls = set()
        for m in IMG_SRC_RE.finditer(text):
            urls.add(m.group(2))
        for m in MD_IMG_RE.finditer(text):
            urls.add(m.group(2))
        for u in urls:
            url_files.setdefault(u, []).append(md)
    return list(url_files.keys()), url_files


def download(url: str, timeout: int = 30) -> tuple[bytes | None, str | None, str | None]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        if r.status_code != 200:
            return None, None, f"HTTP {r.status_code}"
        ct = r.headers.get("Content-Type", "")
        data = r.content
        if len(data) == 0:
            return None, None, "empty body"
        return data, ct, None
    except Exception as e:
        return None, None, str(e)[:200]


def make_s3(creds: dict):
    return boto3.client(
        "s3",
        endpoint_url=creds["endpoint"],
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
        region_name="auto",
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    )


def upload(s3, creds: dict, key: str, body: bytes, content_type: str) -> None:
    s3.put_object(
        Bucket=creds["bucket"],
        Key=key,
        Body=body,
        ContentType=content_type or "application/octet-stream",
        CacheControl="public, max-age=31536000, immutable",
    )


def rewrite_files(url_to_new: dict[str, str], url_to_files: dict[str, list[Path]]) -> int:
    """Replace URLs in every affected md file. Returns count of files changed."""
    changed_files: set[Path] = set()
    for url, new_url in url_to_new.items():
        for f in url_to_files.get(url, []):
            changed_files.add(f)

    n = 0
    for f in changed_files:
        original = f.read_text(encoding="utf-8")
        text = original
        for url, new_url in url_to_new.items():
            if url in text:
                text = text.replace(url, new_url)
        if text != original:
            f.write_text(text, encoding="utf-8")
            n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="scan only, no upload")
    args = ap.parse_args()

    creds = load_creds()
    manifest = load_manifest()

    urls, url_to_files = collect_urls()
    print(f"Found {len(urls)} unique URLs across {sum(len(v) for v in url_to_files.values())} usages")

    if args.dry_run:
        for u in urls[:30]:
            print(f"  {u}")
        if len(urls) > 30:
            print(f"  ... and {len(urls) - 30} more")
        return

    s3 = make_s3(creds)
    public_base = creds["public_base"].rstrip("/")
    prefix = creds.get("key_prefix", "").strip("/")

    new_successes: dict[str, str] = {}
    failures: list[tuple[str, str]] = []

    for i, url in enumerate(urls, 1):
        existing = manifest.get(url)
        if existing and existing.get("status") == "ok":
            # Already uploaded — reuse mapping
            new_successes[url] = existing["public_url"]
            continue

        print(f"[{i}/{len(urls)}] {url[:120]}")
        data, ct, err = download(url)
        if err:
            print(f"  DOWNLOAD FAIL: {err}")
            manifest[url] = {"status": "fail", "error": err, "attempts": (existing or {}).get("attempts", 0) + 1}
            failures.append((url, err))
            continue

        ext = guess_ext(url, ct)
        key_base = url_key(url, ext)
        key = f"{prefix}/{key_base}" if prefix else key_base

        try:
            upload(s3, creds, key, data, ct or mimetypes.guess_type(url)[0] or "application/octet-stream")
        except Exception as e:
            print(f"  UPLOAD FAIL: {e}")
            manifest[url] = {"status": "fail", "error": f"upload: {e}", "attempts": (existing or {}).get("attempts", 0) + 1}
            failures.append((url, str(e)[:200]))
            continue

        public_url = f"{public_base}/{key}"
        manifest[url] = {"status": "ok", "key": key, "public_url": public_url, "bytes": len(data), "ct": ct or ""}
        new_successes[url] = public_url
        print(f"  OK -> {public_url}")

        # checkpoint manifest every 10 uploads
        if i % 10 == 0:
            save_manifest(manifest)

    save_manifest(manifest)

    files_changed = rewrite_files(new_successes, url_to_files)
    print(f"\n=== done: uploaded {len(new_successes)} URLs, rewrote {files_changed} md files, {len(failures)} failure(s) ===")
    if failures:
        print("\nFailures (left as external URLs in markdown):")
        for u, e in failures:
            print(f"  {e}  <-  {u[:150]}")


if __name__ == "__main__":
    main()
