---
name: import-doc-handbook
description: Use when the user pastes a doc.16781678.xyz URL (e.g. /joyflix, /gpt-image2, /nanobanana) and asks to import the whole handbook into this project — places content under content/docs/<slug>/, rehosts every external image on Cloudflare R2, registers the handbook in the home/blog/header/middleware so it shows up in the UI, and ships via git push for auto-deploy on Vercel.
---

# Import doc.16781678.xyz Handbook → R2 → Vercel

End-to-end: a `https://doc.16781678.xyz/<slug>` URL turns into a fully wired, publicly browsable handbook on the production blog. The two scripts (`fetch_doc_sites.py`, `migrate_images.py`, `fix_heading_links.py`) do the heavy lifting — this skill is the **must-do checklist around them**, because every step that's *not* in a script has been forgotten at least once and broken the page.

## TL;DR — one-shot path

Once you have `<slug>` and `<Chinese title>`:

```bash
# 1. Register slug (manual edit, see Phase 2)
# 2. Fetch + transform + migrate images + sanitize headings:
python scripts/fetch_doc_sites.py <slug>
python scripts/migrate_images.py
python scripts/fix_heading_links.py
# 3. Wire UI (manual edits, see Phase 5 — 4 files)
# 4. Verify clean:
taskkill //F //IM node.exe ; rm -rf .next .source ; pnpm dev    # Windows
# rm -rf .next .source && pnpm dev                              # macOS/Linux
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/docs/<slug>/getting-started/readme
# 5. Ship:
git add scripts/fetch_doc_sites.py \
        src/components/docs/dynamic-app-name.tsx \
        src/middleware.ts \
        src/app/[locale]/\(landing\)/page.tsx \
        src/app/[locale]/\(landing\)/blog/page.tsx \
        content/docs/<slug>
git commit -m "feat(docs): import <Slug> handbook with R2-hosted images"
git push origin main
```

If anything looks off, walk the phases below — each has a verify command.

## Phase 1 — Validate the input

- Confirm the URL is the **handbook root** (one path segment: `/gpt-image2`), not a leaf article (`/gpt-image2/payment/foo`). If it's a leaf, ask the user whether they want just that page or the whole site.
- Pick:
  - `<slug>` — the URL path segment exactly as written (lowercase, hyphenated).
  - `<Chinese title>` — usually `"<ProductName> 手册"`.
- `curl -s https://doc.16781678.xyz/<slug> | head -50` — confirm the site exists and is the expected product.

## Phase 2 — Register the slug in `fetch_doc_sites.py`

Edit `scripts/fetch_doc_sites.py`, append to `SITE_TITLES`:

```py
SITE_TITLES = {
    ...,
    "<slug>": "<Chinese title>",
}
```

The script falls back to `slug.title()` if missing, but the Chinese title shows up in `meta.json` and the UI, so add it.

## Phase 3 — Fetch, transform, migrate, sanitize

Run in order — each is idempotent:

```bash
python scripts/fetch_doc_sites.py <slug>     # writes content/docs/<slug>/**/*.mdx + meta.json
python scripts/migrate_images.py             # uploads external images to R2 + rewrites mdx
python scripts/fix_heading_links.py          # fixes <a>-in-<a> hydration errors in headings
```

Expectations:

- `harvested N urls` then `[<cat>] N page(s)` per category. **`[fail]` lines on truncated paths** (e.g. `/payment/paypa` when the real page is `/payment/paypal-cn-person`) are normal — the harvester picks up partial sidebar hits and they 404. Real failures (a unique slug returning 404) need investigation.
- `migrate_images.py`: `OK ->` lines for each image, plus possibly a few `DOWNLOAD FAIL: HTTP 404` for dead `github.com/user-attachments/...` links — those stay external (source already has dead links).
- `fix_heading_links.py`: prints `[N] <file>` for each rewritten heading. Zero modifications is fine if the source had clean headings.

Verify **zero remaining external images** for the new slug:

```bash
python -c "import re,pathlib; root=pathlib.Path('content/docs/<slug>'); ext=[m.group(1) or m.group(2) for f in root.rglob('*.mdx') for m in re.finditer(r'<img[^>]*src=\"(https?://[^\"]+)\"|!\[[^\]]*\]\((https?://[^)\s]+)', f.read_text(encoding='utf-8')) if 'pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev' not in (m.group(1) or m.group(2))]; print('external left:', len(ext))"
```

Should print `external left: 0` (or only known dead user-attachments links).

Auto-handled by `fetch_doc_sites.py`:
- `content/docs/<slug>/meta.json` includes `"root": true` (required — without it fumadocs merges this folder into the parent docs tree and the sidebar shows AI 出海手册 instead of the handbook).
- Internal links `/cat/page` rewritten to `/docs/<slug>/cat/page`.
- URL segment `frequently-asked-questions` mapped to local folder `faq`.

## Phase 4 — (Skim the output)

Quick eye-check of `content/docs/<slug>/index.mdx` and `<slug>/meta.json`:

- `meta.json` should be `{"title":"...","root":true,"pages":[...]}`.
- `index.mdx` should have a YAML frontmatter with `title`.

## Phase 5 — Wire the slug into the UI (4 files, all required)

The UI has **four hardcoded lists** that are NOT auto-derived from `content/docs/`. Skipping any one leaves the handbook half-broken (browsable by direct URL but invisible in the cards/header).

| File | What to edit | Why |
|---|---|---|
| `src/components/docs/dynamic-app-name.tsx` | append `'<slug>': '<Chinese title>',` to `HANDBOOK_TITLES` | header shows the Chinese name instead of the raw slug |
| `src/middleware.ts` | add `\|<slug>` to the `isHandbookRoot` regex | root URL `/docs/<slug>` skips Set-Cookie cache so its redirect to the deep page isn't cached stale |
| `src/app/[locale]/(landing)/page.tsx` | append a card to `featuredDocs` (**no** `target` field — match the existing entries here) | shows on the home page card grid |
| `src/app/[locale]/(landing)/blog/page.tsx` | append a card to `featuredDocs` (**with** `target: '_self'` — match the existing entries here) | shows on `/blog` card grid |

Card object template:
```ts
{
  id: 'docs-<slug>',
  slug: 'docs-<slug>',
  title: '<Chinese title>',
  description: '<one-sentence Chinese description in the same style as siblings>',
  url: '/docs/<slug>/getting-started/readme',
  // target: '_self',   // only on (landing)/blog/page.tsx
  isRecommended: true,
}
```

## Phase 6 — Local sanity check

Turbopack does **not** fully invalidate `.next` / `.source` when a whole content tree is added — every `/docs/*` deep route can 404 with a stale cache. Always wipe before validating:

```bash
# Windows
taskkill //F //IM node.exe ; rm -rf .next .source ; pnpm dev
# macOS/Linux
rm -rf .next .source && pnpm dev
```

Then verify:

```bash
curl -s -o /dev/null -w "/docs/<slug>/getting-started/readme = %{http_code}\n" \
  http://localhost:3000/docs/<slug>/getting-started/readme
# expect 200; if 404, an existing handbook (e.g. joyflix) almost certainly 404s too — you skipped the wipe
```

In a real browser, also check:

- Home `/` and `/blog` show the new card.
- Sidebar on a deep page (e.g. `/docs/<slug>/payment/...`) lists the handbook's own categories — **not** "AI 出海手册" / `must-read` / `ideas` (would mean `root: true` didn't take).
- DevTools console has no `<a> cannot be a descendant of <a>` hydration warning (would mean `fix_heading_links.py` missed a heading).

## Phase 7 — Ship

```bash
git add scripts/fetch_doc_sites.py \
        src/components/docs/dynamic-app-name.tsx \
        src/middleware.ts \
        src/app/[locale]/\(landing\)/page.tsx \
        src/app/[locale]/\(landing\)/blog/page.tsx \
        content/docs/<slug>
git commit -m "feat(docs): import <Slug> handbook with R2-hosted images"
git push origin main
```

Do **not** stage:
- `.claude/scheduled_tasks.lock` (transient harness lock)
- `scripts/image_migration_manifest.json` (gitignored — manifest of uploaded R2 keys)

Vercel auto-deploys on push to `main` (~3 min). Check status:

```bash
curl -s https://api.github.com/repos/<owner>/<repo>/commits/<sha>/status | python -c "import sys,json; d=json.load(sys.stdin); [print(s['context'],s['state'],s.get('target_url','')) for s in d['statuses']]"
```

## Reference: URL segment → local folder

`fetch_doc_sites.py` rewrites these:

| URL segment | Local folder | Sidebar title |
|---|---|---|
| `getting-started` | `getting-started` | 快速开始 |
| `configuration` | `configuration` | 配置指南 |
| `payment` | `payment` | 支付集成 |
| `deployment` | `deployment` | 部署指南 |
| `video-tutorials` | `video-tutorials` | 视频教程 |
| `frequently-asked-questions` | `faq` | 常见问题 |
| `others` | `others` | 其他 |

## Common pitfalls

| Symptom | Root cause | Fix |
|---|---|---|
| `harvested 0 urls` | Wrong slug | `curl https://doc.16781678.xyz/<slug>` to verify the URL exists |
| `[fail] /<slug>/<cat>/<truncated>` | Harvester regex matched a partial sidebar link | Ignore — full URL succeeds for the same page |
| `migrate_images.py: missing scripts/.r2-creds.json` | R2 credentials file absent | The repo has it; if missing on this machine, ask user — do not commit creds |
| MDX parse error on a specific file | Unusual JSX/HTML in source | Hand-escape `{`, `<`, smart quotes in that file's prose |
| Vercel build excludes `*.md` | Old `vercel.json` regression (fixed in `8032ad4`) | Don't re-add `*.md` to ignore patterns |
| Local `/docs/<slug>/...` is 404 **and so is `/docs/joyflix/...`** | Stale Turbopack cache | `rm -rf .next .source && pnpm dev` |
| Header shows English slug, not Chinese title | Forgot `HANDBOOK_TITLES` | Phase 5, file 1 |
| Handbook missing from home/blog card grid | Forgot one or both `featuredDocs` lists | Phase 5, files 3+4 |
| Sidebar shows AI 出海手册 / `must-read` / `ideas` under the new slug | `meta.json` missing `"root": true` | `fetch_doc_sites.py` adds it now; backfill manually for handbooks imported before that fix |
| Console: `<a> cannot be a descendant of <a>` / hydration error | A heading contains `[text](url)` or a bare URL | `python scripts/fix_heading_links.py` (always run after fetch) |
| Vercel deploy looks "stuck" | It already finished — you're looking at a stale browser tab | Check `repos/<owner>/<repo>/commits/<sha>/status` via the GitHub REST API |

## Files this skill touches

- `scripts/fetch_doc_sites.py` — 1 line in `SITE_TITLES`
- `src/components/docs/dynamic-app-name.tsx` — 1 line in `HANDBOOK_TITLES`
- `src/middleware.ts` — 1 token added to the handbook-root regex
- `src/app/[locale]/(landing)/page.tsx` — 1 card object appended to `featuredDocs`
- `src/app/[locale]/(landing)/blog/page.tsx` — 1 card object appended to `featuredDocs`
- `content/docs/<slug>/**` — created by the fetch script
- `scripts/image_migration_manifest.json` — rewritten by image migrator (gitignored)
